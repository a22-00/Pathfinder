from flask import Flask, request, jsonify, render_template, session
import json
import re
import anthropic
import os
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_default_secret_key_123!@#")

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

client = None
if ANTHROPIC_API_KEY:
    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    except Exception as e:
        print(f"Error initializing client: {e}")
        client = None
else:
    print("ANTHROPIC_API_KEY not found")

user_sessions = {}

@app.route('/')
def home():
    return render_template('Pathfinder.html')

@app.route('/testchat.html')
def test():
    return render_template('testchat.html')

@app.route('/assessment.html', methods=['GET'])
def student_assessment():
    return render_template('assessment.html')

@app.route('/assessment')
def assessment():
    return render_template('assessment.html')

@app.route('/learning-plan')
def learning_plan():
    return render_template('learning_plan.html')

def generate_questions(topic):
    prompt = f"""Generate 25 multiple-choice questions about {topic}. Format:
    
    Question X: [Question text]
    A) [Option A]
    B) [Option B] 
    C) [Option C]
    D) [Option D]
    Correct Answer: [Letter]"""
    
    try:
        if client is None:
            print("❌ Claude client is not initialized.")
            return []
            
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=3000,
            temperature=0.7,
            system="You are a helpful AI assistant that generates educational assessment questions.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        questions_text = response.content[0].text
        return parse_questions(questions_text)
    except Exception as e:
        print(f"Error generating questions: {e}")
        return []

def parse_questions(questions_text):
    """Parse the generated questions text into structured data"""
    questions = []
    question_blocks = re.split(r'Question \d+:', questions_text)[1:]  # Skip first empty element
    
    for i, block in enumerate(question_blocks):
        if i >= 25:  
            break
            
        lines = [line.strip() for line in block.strip().split('\n') if line.strip()]
        if len(lines) < 6: 
            continue
            
        question_text = lines[0]
        options = {}
        correct_answer = None
        
        for line in lines[1:]:
            if line.startswith(('A)', 'B)', 'C)', 'D)')):
                letter = line[0]
                text = line[3:].strip()
                options[letter] = text
            elif line.startswith('Correct Answer:'):
                correct_answer = line.split(':')[1].strip()
        
        if len(options) == 4 and correct_answer:
            questions.append({
                'id': i + 1,
                'question': question_text,
                'options': options,
                'correct_answer': correct_answer
            })
    
    return questions

def generate_learning_plan(topic, score, total_questions, incorrect_answers):
    percentage = (score / total_questions) * 100
    
    prompt = f"""Create learning plan for {score}/{total_questions} ({percentage:.1f}%) on {topic}.
    
Weak areas: {chr(10).join([f"- {item['question']}" for item in incorrect_answers[:3]])}

Provide: knowledge assessment, focus topics, resources, 4-week schedule, exercises."""
    
    try:
        if client is None:
            print("❌ Claude client is not initialized.")
            return "Unable to generate learning plan at this time."
            
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=2000,
            temperature=0.7,
            system="You are a helpful AI assistant that creates personalized learning plans.",
            messages=[{"role": "user", "content": prompt}]
        )
        
        return response.content[0].text
    except Exception as e:
        print(f"Error generating learning plan: {e}")
        return "Unable to generate learning plan at this time."

@app.route('/start-assessment', methods=['POST'])
def start_assessment():
    """Start a new assessment with a topic"""
    data = request.json
    topic = data.get('topic', '').strip()
    
    if not topic:
        return jsonify({'error': 'Topic is required'}), 400
    
    # Generate session ID
    session_id = f"session_{len(user_sessions) + 1}"
    
    # Generate questions
    questions = generate_questions(topic)
    
    if not questions:
        return jsonify({'error': 'Failed to generate questions'}), 500
    
    # Store session data
    user_sessions[session_id] = {
        'topic': topic,
        'questions': questions,
        'current_question': 0,
        'score': 0,
        'answers': [],
        'incorrect_answers': []
    }
    
    return jsonify({
        'session_id': session_id,
        'topic': topic,
        'total_questions': len(questions),
        'first_question': questions[0] if questions else None
    })

@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    """Submit an answer for the current question"""
    data = request.json
    session_id = data.get('session_id')
    answer = data.get('answer', '').strip().upper()
    
    if session_id not in user_sessions:
        return jsonify({'error': 'Invalid session'}), 400
    
    session_data = user_sessions[session_id]
    current_q_index = session_data['current_question']
    
    if current_q_index >= len(session_data['questions']):
        return jsonify({'error': 'Assessment already completed'}), 400
    
    current_question = session_data['questions'][current_q_index]
    correct_answer = current_question['correct_answer']
    is_correct = answer == correct_answer
    
    # Record the answer
    session_data['answers'].append({
        'question_id': current_question['id'],
        'user_answer': answer,
        'correct_answer': correct_answer,
        'is_correct': is_correct
    })
    
    if is_correct:
        session_data['score'] += 1
    else:
        session_data['incorrect_answers'].append({
            'question': current_question['question'],
            'user_answer': answer,
            'correct_answer': correct_answer,
            'correct_option': current_question['options'][correct_answer]
        })
    
    # Move to next question
    session_data['current_question'] += 1
    
    # Check if assessment is complete
    if session_data['current_question'] >= len(session_data['questions']):
        # Assessment completed
        learning_plan = generate_learning_plan(
            session_data['topic'],
            session_data['score'],
            len(session_data['questions']),
            session_data['incorrect_answers']
        )
        
        return jsonify({
            'completed': True,
            'score': session_data['score'],
            'total': len(session_data['questions']),
            'percentage': (session_data['score'] / len(session_data['questions'])) * 100,
            'learning_plan': learning_plan,
            'is_correct': is_correct,
            'correct_answer': correct_answer,
            'explanation': current_question['options'][correct_answer]
        })
    else:
        # Return next question
        next_question = session_data['questions'][session_data['current_question']]
        return jsonify({
            'completed': False,
            'is_correct': is_correct,
            'correct_answer': correct_answer,
            'explanation': current_question['options'][correct_answer],
            'next_question': next_question,
            'progress': {
                'current': session_data['current_question'] + 1,
                'total': len(session_data['questions'])
            }
        })

@app.route('/test', methods=['POST'])
def quiz():
    """Legacy endpoint for backward compatibility"""
    data = request.json
    user_message = data.get("message", "").strip()
    
    # Simple response for testing
    return jsonify({
        "response": f"You said: {user_message}. This is the legacy endpoint.",
        "score": 0
    })

if __name__ == '__main__':
    app.run(debug=True) 