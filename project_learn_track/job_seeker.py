import os
import sys
import uuid
from flask import Flask, render_template, request, redirect, url_for, session, jsonify, flash
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from dotenv import load_dotenv
import anthropic
from pytrends.request import TrendReq
import pandas as pd
import time 
import re
import json
import pickle
from datetime import datetime, timedelta
import random

sys.path.append(os.path.dirname(__file__))
from models import (
    db, User, ChatConversation, ChatMessage, Assessment, Recommendation, 
    UserActivity, TrendData, create_user, log_user_activity, 
    get_user_recommendations, create_chat_conversation, add_chat_message
)
from forms import LoginForm, RegistrationForm, ProfileForm, ChangePasswordForm, QuickSetupForm

try:
    from personalization import personalization_engine
except ImportError:
    personalization_engine = None

load_dotenv()

app = Flask(__name__, template_folder='../templates')
app.secret_key = os.getenv("FLASK_SECRET_KEY", "dev_default_secret_key_123!@#")

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///pathfinder_pro.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'auth_login'
login_manager.login_message = 'Please log in to access this page.'
login_manager.login_message_category = 'info'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = None

print("=" * 60)
print("🤖 CLAUDE API INITIALIZATION")
print("=" * 60)

if ANTHROPIC_API_KEY:
    print("✅ API Key loaded from environment")
    print(f"📏 API Key validation: {'✅ Valid format' if len(ANTHROPIC_API_KEY) > 20 else '❌ Invalid format'}")
    
    try:
        print("🔌 Initializing Claude client...")
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        print("✅ Claude client initialized successfully!")
        
        print("🧪 Testing Claude API connection...")
        test_response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=50,
            messages=[{"role": "user", "content": "Hello, are you working?"}]
        )
        
        if test_response and test_response.content:
            print("✅ Claude API test successful!")
            print(f"📝 Test response: {test_response.content[0].text[:50]}...")
        else:
            print("⚠️ Claude API test returned empty response")
            
    except anthropic.AuthenticationError as e:
        print(f"❌ Authentication Error: {e}")
        print("🔑 Please check your ANTHROPIC_API_KEY in the .env file")
        client = None
    except anthropic.APIConnectionError as e:
        print(f"❌ API Connection Error: {e}")
        print("🌐 Please check your internet connection")
        client = None
    except AttributeError as e:
        print(f"⚠️ Anthropic version compatibility issue: {e}")
        print("📦 This may be due to an outdated anthropic library")
        print("🔄 Try running: pip install --upgrade anthropic")
        client = None
    except Exception as e:
        print(f"❌ Error initializing Anthropic client: {e}")
        print(f"🔧 Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        client = None
else:
    print("❌ ANTHROPIC_API_KEY not found in environment variables")
    print("🔧 Please add ANTHROPIC_API_KEY to your .env file")
    print("💡 Get your API key from: https://console.anthropic.com/")

print("=" * 60)
print(f"🎯 Final Status: {'✅ READY' if client else '❌ FALLBACK MODE'}")
print("=" * 60)

with app.app_context():
    db.create_all()
    print("✅ Database tables created successfully!")

def generate_llm_content(prompt_text, model="claude-3-haiku-20240307", max_tokens=1500):
    """Generate content using Claude API with enhanced error handling and debugging"""
    
    print(f"🤖 Generating LLM content - Prompt length: {len(prompt_text)} chars")
    print(f"🔑 API Key status: {'✅ Present' if ANTHROPIC_API_KEY else '❌ Missing'}")
    print(f"🔌 Client status: {'✅ Initialized' if client else '❌ Not initialized'}")
    
    if client is None:
        print("❌ Claude client not initialized - using fallback")
        return get_fallback_content(prompt_text)
    
    if not ANTHROPIC_API_KEY:
        print("❌ ANTHROPIC_API_KEY not found in environment - using fallback")
        return get_fallback_content(prompt_text)
    
    if len(ANTHROPIC_API_KEY) < 20:
        print("❌ Invalid API key format - using fallback")
        return get_fallback_content(prompt_text)
    
    try:
        print("🚀 Calling Claude API...")
        
        system_prompt = """You are an expert AI career assistant and coach. Provide helpful, specific, and actionable career advice. 

Key guidelines:
- Give personalized responses based on the user's profile and context
- Include specific examples, actionable steps, and practical recommendations
- Use a professional but friendly tone
- Structure your responses clearly with headers and bullet points where appropriate
- Provide current industry insights when relevant
- Always be encouraging and supportive while being realistic

Format your responses in a clear, easy-to-read structure."""

        try:
            response = client.messages.create(
                model=model,
                max_tokens=max_tokens,
                temperature=0.7,
                system=system_prompt,
                messages=[{"role": "user", "content": prompt_text}]
            )
        except AttributeError:
            print("⚠️ Using fallback API method for older anthropic version")
            response = client.completions.create(
                model=model,
                prompt=f"System: {system_prompt}\n\nHuman: {prompt_text}\n\nAssistant:",
                max_tokens_to_sample=max_tokens,
                temperature=0.7
            )
        
        if not response:
            print("❌ Empty response from Claude API")
            return get_fallback_content(prompt_text)
        
        if hasattr(response, 'content') and response.content:
            content = response.content[0].text.strip()
        elif hasattr(response, 'completion'):
            content = response.completion.strip()
        else:
            print("❌ Unexpected response format from Claude API")
            return get_fallback_content(prompt_text)
        
        print(f"✅ Claude API success - Response length: {len(content)} chars")
        
        if len(content) < 50:
            print("⚠️ Response too short, using fallback")
            return get_fallback_content(prompt_text)
        
        return content
        
    except anthropic.AuthenticationError as e:
        print(f"❌ Claude API Authentication Error: {e}")
        print("🔑 Please check your ANTHROPIC_API_KEY")
        return get_fallback_content(prompt_text)
    
    except anthropic.RateLimitError as e:
        print(f"❌ Claude API Rate Limit Error: {e}")
        return get_fallback_content(prompt_text)
    
    except anthropic.APIConnectionError as e:
        print(f"❌ Claude API Connection Error: {e}")
        return get_fallback_content(prompt_text)
    
    except AttributeError as e:
        print(f"⚠️ Claude API Attribute Error (version compatibility): {e}")
        print("📦 This may indicate an anthropic library version issue")
        return get_fallback_content(prompt_text)
    
    except Exception as e:
        print(f"❌ Claude API Unexpected Error: {e}")
        print(f"🔧 Error type: {type(e).__name__}")
        import traceback
        traceback.print_exc()
        return get_fallback_content(prompt_text)

def get_fallback_content(prompt_text):
    """Provide intelligent fallback content when Claude API is unavailable"""
    print("🔄 Using intelligent fallback content")
    
    prompt_lower = prompt_text.lower()
    
    if any(keyword in prompt_lower for keyword in ['salary', 'compensation', 'pay', 'money']):
        return """## 💰 Salary & Compensation Guidance

I'd love to help with salary-related questions! Here's some general guidance:

**🎯 Salary Research:**
- Use Glassdoor, PayScale, and LinkedIn Salary Insights
- Check industry reports from recruiting firms
- Consider location, company size, and experience level

**💼 Negotiation Tips:**
- Research market rates thoroughly before negotiations
- Present your value proposition clearly
- Consider total compensation (benefits, equity, PTO)
- Practice your negotiation conversation

**📈 Factors Affecting Compensation:**
- Years of relevant experience
- Technical skills and certifications
- Industry and company size
- Geographic location
- Current market demand

*For personalized salary advice, I'd need more details about your specific role, experience, and location!*"""

    elif any(keyword in prompt_lower for keyword in ['interview', 'preparation', 'questions']):
        return """## 🎯 Interview Preparation Guide

Here's a comprehensive interview preparation strategy:

**📋 Before the Interview:**
- Research the company thoroughly (mission, values, recent news)
- Review the job description and match your experience
- Prepare STAR method examples for behavioral questions
- Practice common technical questions for your field

**🗣️ Common Interview Questions:**
- "Tell me about yourself" - Prepare a 2-minute professional summary
- "Why do you want this role?" - Connect your goals to the position
- "Describe a challenge you overcame" - Use specific examples
- "Where do you see yourself in 5 years?" - Show alignment with growth

**❓ Questions to Ask Them:**
- "What does success look like in this role?"
- "What are the biggest challenges facing the team?"
- "How do you support professional development?"

**🎭 Day of Interview:**
- Arrive 10-15 minutes early
- Bring copies of your resume
- Dress appropriately for company culture
- Follow up with a thank-you email within 24 hours

*Would you like me to help with specific interview scenarios or questions?*"""

    elif any(keyword in prompt_lower for keyword in ['trend', 'market', 'industry', 'future']):
        return """## 📊 Industry Trends & Market Insights

Here are some current trends across tech and professional industries:

**🚀 Technology Trends:**
- AI/ML integration across all industries
- Cloud computing and DevOps skills in high demand
- Cybersecurity becoming critical everywhere
- Remote work technologies and management
- Data science and analytics growth

**💼 Workplace Trends:**
- Hybrid and remote work normalization
- Focus on work-life balance and mental health
- Skills-based hiring over degree requirements
- Continuous learning and upskilling emphasis
- Diversity, equity, and inclusion priorities

**🎯 In-Demand Skills:**
- Programming languages: Python, JavaScript, Go
- Cloud platforms: AWS, Azure, Google Cloud
- Data tools: SQL, Tableau, Power BI
- Soft skills: Communication, adaptability, leadership
- AI tools and prompt engineering

**📈 Career Growth Areas:**
- Renewable energy and sustainability
- Healthcare technology
- FinTech and digital banking
- E-commerce and digital marketing
- EdTech and online learning

*What specific industry or trend would you like me to dive deeper into?*"""

    elif any(keyword in prompt_lower for keyword in ['skill', 'learn', 'development', 'course']):
        return """## 🎓 Skill Development Roadmap

Let me help you plan your learning journey:

**🔍 Skills Assessment:**
- Identify your current skill level
- Research job requirements in your target roles
- Find the gap between current and desired skills
- Prioritize skills based on market demand

**📚 Learning Resources:**
- **Online Courses:** Coursera, Udemy, edX, Pluralsight
- **Free Resources:** YouTube, freeCodeCamp, Khan Academy
- **Hands-on Practice:** GitHub projects, Kaggle, HackerRank
- **Certifications:** AWS, Google, Microsoft, industry-specific

**🗓️ Learning Strategy:**
- Set SMART goals (Specific, Measurable, Achievable)
- Dedicate consistent time daily (even 30 minutes helps)
- Practice with real projects and portfolios
- Join communities and find mentors
- Apply new skills immediately at work

**💡 Popular Skill Paths:**
- **Data Science:** Python, SQL, Statistics, Machine Learning
- **Web Development:** HTML/CSS, JavaScript, React, Node.js
- **Cloud Computing:** AWS/Azure basics, Docker, Kubernetes
- **Digital Marketing:** SEO, Analytics, Social Media, Content

*What specific skills are you looking to develop? I can provide a more targeted learning plan!*"""

    elif any(keyword in prompt_lower for keyword in ['resume', 'cv', 'application']):
        return """## 📄 Resume Optimization Guide

Here's how to create a standout resume:

**🎯 Resume Structure:**
- **Header:** Name, phone, email, LinkedIn, portfolio (if relevant)
- **Summary:** 2-3 lines highlighting your value proposition
- **Experience:** Focus on achievements, not just responsibilities
- **Skills:** Technical and soft skills relevant to target role
- **Education:** Include certifications and relevant coursework

**✨ Writing Tips:**
- Use action verbs (achieved, developed, led, improved)
- Quantify results with numbers and percentages
- Tailor keywords to match job descriptions
- Keep it concise (1-2 pages for most professionals)
- Use consistent formatting and clean design

**🔍 ATS Optimization:**
- Use standard section headers
- Include relevant keywords from job postings
- Avoid images, graphics, or unusual fonts
- Save as PDF and Word versions
- Test readability with ATS checkers

**📊 Common Mistakes to Avoid:**
- Generic objectives instead of targeted summaries
- Listing duties instead of accomplishments
- Including irrelevant work experience
- Typos and grammatical errors
- Using outdated email addresses

*Would you like me to review specific sections of your resume or help with targeting it for particular roles?*"""

    else:
        return """## 🤖 AI Career Assistant

I'm here to help with your career development! While I'm currently running in offline mode, I can still provide valuable guidance on:

**📊 Career Planning:**
- Industry insights and trend analysis
- Career transition strategies
- Goal setting and professional development planning
- Skills gap analysis and learning roadmaps

**🎯 Job Search Support:**
- Resume writing and optimization
- Interview preparation and practice
- LinkedIn profile enhancement
- Networking strategies and tips

**💼 Professional Development:**
- Skill development recommendations
- Certification guidance
- Portfolio building tips
- Personal branding strategies

**💰 Compensation & Negotiation:**
- Salary research methods
- Negotiation preparation
- Benefits evaluation
- Market value assessment

*Please ask me specific questions about any of these topics, and I'll provide detailed, actionable advice to help you succeed in your career journey!*

**Example questions you could ask:**
- "How do I transition from marketing to data science?"
- "What skills should I learn for remote software development?"
- "How do I negotiate a salary increase?"
- "What's the best way to network in the tech industry?"

*What would you like to explore first?*"""

@app.route('/auth/login', methods=['GET', 'POST'])
def auth_login():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username.data) | (User.email == form.username.data)
        ).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            user.last_login = datetime.utcnow()
            db.session.commit()
            
            log_user_activity(user.id, 'login', 'User logged in')
            
            flash('Welcome back!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('dashboard'))
        else:
            flash('Invalid username/email or password', 'error')
    
    return render_template('auth/login.html', form=form)

@app.route('/auth/register', methods=['GET', 'POST'])
def auth_register():
    if current_user.is_authenticated:
        return redirect(url_for('dashboard'))
    
    form = RegistrationForm()
    
    if request.method == 'POST':
        print(f"🔍 Registration attempt:")
        print(f"   Form data: {request.form}")
        print(f"   Form valid: {form.validate_on_submit()}")
        if form.errors:
            print(f"   Form errors: {form.errors}")
    
    if form.validate_on_submit():
        try:
            print(f"✅ Creating user: {form.username.data} ({form.email.data})")
            user = create_user(
                username=form.username.data,
                email=form.email.data,
                password=form.password.data,
                first_name=form.first_name.data,
                last_name=form.last_name.data
            )
            
            print(f"✅ User created successfully: {user.id}")
            login_user(user)
            flash('Registration successful! Welcome to Pathfinder Pro!', 'success')
            
            log_user_activity(user.id, 'register', 'User registered')
            
            print(f"✅ Redirecting to setup_profile")
            return redirect(url_for('setup_profile'))
        except Exception as e:
            flash('Registration failed. Please try again.', 'error')
            print(f"❌ Registration error: {e}")
            import traceback
            traceback.print_exc()
    
    return render_template('auth/register.html', form=form)

@app.route('/auth/logout')
@login_required
def auth_logout():
    log_user_activity(current_user.id, 'logout', 'User logged out')
    logout_user()
    flash('You have been logged out.', 'info')
    return redirect(url_for('home'))

@app.route('/setup', methods=['GET', 'POST'])
@login_required
def setup_profile():
    form = QuickSetupForm()
    
    if request.method == 'POST':
        print(f"🔍 Setup form submission:")
        print(f"   Form data: {request.form}")
        print(f"   Form valid: {form.validate_on_submit()}")
        if form.errors:
            print(f"   Form errors: {form.errors}")
    
    if form.validate_on_submit():
        try:
            print(f"✅ Updating user profile: {current_user.username}")
            current_user.profession = form.profession.data
            current_user.experience_level = form.experience_level.data
            current_user.career_goals = form.career_goals.data
            
            db.session.commit()
            print(f"✅ Profile updated successfully")
            
            log_user_activity(current_user.id, 'setup', 'Profile setup completed')
            
            flash('Profile setup complete!', 'success')
            return redirect(url_for('dashboard'))
        except Exception as e:
            db.session.rollback()
            flash('An error occurred while setting up your profile. Please try again.', 'error')
            print(f"❌ Setup error: {e}")
            import traceback
            traceback.print_exc()
    
    return render_template('auth/setup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    try:
        assessment_completed = request.args.get('assessment_completed') == 'true'
        
        try:
            stats = current_user.get_assessment_stats()
            print(f"📈 Stats for user {current_user.id}: {stats}")
        except Exception as e:
            print(f"❌ Error getting stats: {e}")
            stats = {'total': 0, 'average_score': 0, 'highest_score': 0}
        
        try:
            recent_activities = UserActivity.query.filter_by(user_id=current_user.id)\
                                                 .order_by(UserActivity.created_at.desc())\
                                                 .limit(5).all()
        except Exception as e:
            print(f"❌ Error getting activities: {e}")
            recent_activities = []
        
        try:
            recent_recommendations = Recommendation.query.filter_by(user_id=current_user.id)\
                                                         .filter_by(is_completed=False)\
                                                         .order_by(Recommendation.priority.asc(), Recommendation.created_at.desc())\
                                                         .limit(3).all()
        except Exception as e:
            print(f"❌ Error getting recommendations: {e}")
            recent_recommendations = []
        
        try:
            conversations = ChatConversation.query.filter_by(user_id=current_user.id)\
                                                 .order_by(ChatConversation.updated_at.desc())\
                                                 .limit(5).all()
        except Exception as e:
            print(f"❌ Error getting conversations: {e}")
            conversations = []
        
        try:
            recent_assessments = Assessment.query.filter_by(user_id=current_user.id)\
                                                .order_by(Assessment.created_at.desc())\
                                                .limit(5).all()
            print(f"✅ Found {len(recent_assessments)} recent assessments for user {current_user.id}")
            
            # Debug: Print assessment details
            for i, assessment in enumerate(recent_assessments):
                print(f"📊 Assessment {i+1}: {assessment.topic} - {assessment.score}/{assessment.total_questions} - {assessment.is_completed}")
                
        except Exception as e:
            print(f"❌ Error getting recent assessments: {e}")
            recent_assessments = []
        
        if assessment_completed:
            flash('🎉 Assessment completed successfully! Check your results below.', 'success')
        
        print(f"✅ Dashboard loaded for user: {current_user.username}")
        return render_template('dashboard/index.html', 
                             user=current_user,
                             stats=stats,
                             recent_activities=recent_activities,
                             recent_recommendations=recent_recommendations,
                             conversations=conversations,
                             activities=recent_activities,
                             recommendations=recent_recommendations,
                             recent_assessments=recent_assessments,
                             assessment_completed=assessment_completed)
    except Exception as e:
        print(f"❌ Dashboard error: {e}")
        import traceback
        traceback.print_exc()
        flash('Error loading dashboard. Please try again.', 'error')
        return redirect(url_for('home'))

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/job-seeker')
def job_seeker_home():
    if current_user.is_authenticated:
        return redirect(url_for('chat_interface'))
    return redirect(url_for('auth_login'))

@app.route('/chat')
@login_required
def chat_interface():
    conversation = ChatConversation.query.filter_by(user_id=current_user.id)\
                                        .order_by(ChatConversation.updated_at.desc())\
                                        .first()
    
    if not conversation:
        conversation = create_chat_conversation(current_user.id, "New Conversation")
    
    messages = ChatMessage.query.filter_by(conversation_id=conversation.id)\
                                .order_by(ChatMessage.created_at.asc()).all()
    
    return render_template('job_seeker_chat.html', 
                         conversation=conversation, 
                         messages=messages,
                         user=current_user)

@app.route('/assessment')
def assessment_page():
    if current_user.is_authenticated:
        return render_template('assessment.html', user=current_user)
    return redirect(url_for('auth_login'))

@app.route('/chat', methods=['POST'])
@login_required
def chat_handler():
    print("\n" + "=" * 60)
    print("💬 CHAT REQUEST RECEIVED")
    print("=" * 60)
    
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        context_data = data.get('context', {})
        query_type = context_data.get('query_type', 'general')
        
        print(f"👤 User: {current_user.username}")
        print(f"📝 Message: {user_message[:100]}..." if len(user_message) > 100 else f"📝 Message: {user_message}")
        print(f"🏷️ Query Type: {query_type}")
        print(f"🔌 Claude Client Status: {'✅ Available' if client else '❌ Unavailable'}")
        
        if not user_message:
            print("❌ Empty message received")
            return jsonify({'error': 'Message cannot be empty'}), 400
        
        conversation_id = data.get('conversation_id')
        if conversation_id:
            conversation = ChatConversation.query.get(conversation_id)
            if not conversation or conversation.user_id != current_user.id:
                return jsonify({'error': 'Invalid conversation'}), 403
        else:
            conversation = create_chat_conversation(current_user.id)
        
        add_chat_message(conversation.id, 'user', user_message)
        
        print("🤖 Building context for AI response...")
        context = build_enhanced_context(current_user, user_message, query_type)
        print(f"📋 Context length: {len(context)} characters")
        
        print("🎯 Generating AI response...")
        ai_response = generate_llm_content(context)
        print(f"✅ AI Response generated: {len(ai_response)} characters")
        print(f"📄 Response preview: {ai_response[:200]}...")
        
        add_chat_message(conversation.id, 'ai', ai_response)
        
        conversation.updated_at = datetime.utcnow()
        if not conversation.title or conversation.title == "New Conversation":
            conversation.title = user_message[:50] + "..." if len(user_message) > 50 else user_message
        
        db.session.commit()
        
        log_user_activity(current_user.id, 'chat', f'Chat message: {user_message[:50]}...')
        
        recommendations = generate_smart_recommendations(user_message, query_type, current_user)
        
        return jsonify({
            'response': ai_response,
            'conversation_id': conversation.id,
            'recommendations': recommendations,
            'query_type': query_type
        })
        
    except Exception as e:
        print(f"Chat handler error: {e}")
        return jsonify({'error': 'An error occurred processing your message'}), 500

def build_enhanced_context(user, message, query_type):
    """Build enhanced context based on query type and user profile"""
    base_context = f"""User Profile:
- Name: {user.get_full_name()}
- Profession: {user.profession or 'Not specified'}
- Experience Level: {user.experience_level or 'Not specified'}
- Skills: {', '.join(user.get_skills_list()) if user.get_skills_list() else 'Not specified'}
- Career Goals: {user.career_goals or 'Not specified'}

Query Type: {query_type}
User Message: {message}"""

    if query_type == 'market_trends':
        context = base_context + """

Please provide detailed, current market trends and industry insights. Include:
- Latest technology trends affecting the user's field
- Job market conditions and growth projections
- Emerging skills in demand
- Salary trends and compensation insights
- Remote work opportunities
- Industry-specific data and statistics where relevant"""

    elif query_type == 'salary_inquiry':
        context = base_context + """

Please provide comprehensive salary and compensation guidance. Include:
- Current salary ranges for the user's role and experience level
- Factors affecting compensation (location, company size, skills)
- Negotiation strategies and tips
- Benefits and total compensation considerations
- Career advancement impact on salary
- Market data and benchmarks"""

    elif query_type == 'interview_prep':
        context = base_context + """

Please provide thorough interview preparation guidance. Include:
- Common interview questions for the user's field
- Technical interview preparation if relevant
- Behavioral interview strategies
- Company research tips
- Questions to ask interviewers
- Post-interview follow-up advice
- Specific preparation based on experience level"""

    elif query_type == 'skill_development':
        context = base_context + """

Please provide detailed skill development recommendations. Include:
- Skills currently in high demand for the user's field
- Learning resources (courses, certifications, books)
- Practical projects to build skills
- Timeline and learning path suggestions
- Skills gap analysis based on career goals
- Industry certifications that add value"""

    elif query_type == 'networking':
        context = base_context + """

Please provide comprehensive networking strategies. Include:
- Industry-specific networking opportunities
- Online and offline networking platforms
- Building meaningful professional relationships
- Networking event strategies
- LinkedIn optimization
- Mentorship opportunities
- Following up and maintaining connections"""

    elif query_type == 'resume_help':
        context = base_context + """

Please provide detailed resume optimization guidance. Include:
- Resume structure and formatting best practices
- Industry-specific resume tips
- Keywords and ATS optimization
- Quantifying achievements and impact
- Tailoring resume for specific roles
- Common resume mistakes to avoid
- Portfolio and additional materials"""

    else:
        context = base_context + """

Please provide helpful, personalized career advice. Be specific to the user's situation and provide actionable insights."""

    return context

def generate_smart_recommendations(message, query_type, user):
    """Generate smart recommendations based on query type and context"""
    recommendations = []
    
    if query_type == 'market_trends':
        recommendations = [
            "Explore trending skills in your industry",
            "Check salary trends for your role",
            "Research emerging technologies",
            "Update your LinkedIn profile with trending keywords"
        ]
    elif query_type == 'salary_inquiry':
        recommendations = [
            "Research salary benchmarks on Glassdoor",
            "Prepare for salary negotiations",
            "Consider total compensation package",
            "Evaluate your current market value"
        ]
    elif query_type == 'interview_prep':
        recommendations = [
            "Practice coding challenges if tech role",
            "Research the company thoroughly",
            "Prepare STAR method responses",
            "Schedule mock interviews"
        ]
    elif query_type == 'skill_development':
        recommendations = [
            "Take a skills assessment",
            "Create a learning schedule",
            "Join relevant online communities",
            "Find a mentor in your field"
        ]
    elif query_type == 'networking':
        recommendations = [
            "Optimize your LinkedIn profile",
            "Attend industry meetups",
            "Join professional associations",
            "Reach out to alumni network"
        ]
    elif query_type == 'resume_help':
        recommendations = [
            "Get resume feedback from professionals",
            "Customize resume for each application",
            "Add quantifiable achievements",
            "Create an online portfolio"
        ]
    else:
        if any(word in message.lower() for word in ['help', 'recommend', 'suggest', 'advice']):
            recommendations = [
                "Take a comprehensive skills assessment",
                "Explore current job market trends",
                "Update your professional profiles",
                "Connect with industry professionals"
            ]
    
    return recommendations

# Persistent session storage
SESSIONS_DIR = os.path.join(os.path.dirname(__file__), '..', 'sessions')
if not os.path.exists(SESSIONS_DIR):
    os.makedirs(SESSIONS_DIR)
    print(f"✅ Created sessions directory: {SESSIONS_DIR}")

class PersistentSessionManager:
    def __init__(self):
        self.sessions_dir = SESSIONS_DIR
        print(f"🗂️ Session manager initialized with directory: {self.sessions_dir}")
    
    def _get_session_file(self, session_id):
        return os.path.join(self.sessions_dir, f"{session_id}.pkl")
    
    def save_session(self, session_id, session_data):
        """Save session to file"""
        try:
            session_file = self._get_session_file(session_id)
            session_data['last_saved'] = datetime.utcnow()
            with open(session_file, 'wb') as f:
                pickle.dump(session_data, f)
            print(f"💾 Session {session_id} saved to file")
            return True
        except Exception as e:
            print(f"❌ Error saving session {session_id}: {e}")
            return False
    
    def load_session(self, session_id):
        """Load session from file"""
        try:
            session_file = self._get_session_file(session_id)
            if not os.path.exists(session_file):
                print(f"📁 Session file not found: {session_id}")
                return None
            
            with open(session_file, 'rb') as f:
                session_data = pickle.load(f)
                
            session_data['last_accessed'] = datetime.utcnow()
            self.save_session(session_id, session_data)
            
            print(f"📂 Session {session_id} loaded from file")
            return session_data
        except Exception as e:
            print(f"❌ Error loading session {session_id}: {e}")
            return None
    
    def delete_session(self, session_id):
        """Delete session file"""
        try:
            session_file = self._get_session_file(session_id)
            if os.path.exists(session_file):
                os.remove(session_file)
                print(f"🗑️ Session {session_id} deleted")
                return True
        except Exception as e:
            print(f"❌ Error deleting session {session_id}: {e}")
        return False
    
    def get_all_sessions(self):
        """Get all session IDs"""
        try:
            session_files = [f for f in os.listdir(self.sessions_dir) if f.endswith('.pkl')]
            return [f[:-4] for f in session_files]  # Remove .pkl extension
        except Exception as e:
            print(f"❌ Error listing sessions: {e}")
            return []
    
    def cleanup_expired_sessions(self, max_age_hours=24):
        """Clean up old session files"""
        try:
            current_time = datetime.utcnow()
            expired_count = 0
    
            for session_id in self.get_all_sessions():
                session_data = self.load_session(session_id)
                if session_data:
                    started_at = session_data.get('started_at', current_time)
                    age_hours = (current_time - started_at).total_seconds() / 3600
                    
                    if age_hours > max_age_hours:
                        self.delete_session(session_id)
                        expired_count += 1
                        print(f"🧹 Expired session {session_id} (age: {age_hours:.1f}h)")
            
            if expired_count == 0:
                print(f"✅ No expired sessions found (max age: {max_age_hours}h)")
            
            return expired_count
        except Exception as e:
            print(f"❌ Error during cleanup: {e}")
            return 0

session_manager = PersistentSessionManager()

user_sessions = {}

def validate_session(session_id):
    """Validate and refresh session if needed"""
    if not session_id:
        return False, "No session ID provided"
    
    session_data = session_manager.load_session(session_id)
    if not session_data:
        print(f"❌ Session {session_id} not found in persistent storage")
        return False, f"Session {session_id} not found - please restart the assessment"
    
    return True, session_data

def generate_questions(topic):
    """Generate assessment questions using Claude"""
    prompt = f"""Generate 25 multiple-choice questions about {topic}. 
Format each question exactly as:

Question X: [question text]
A) [option A]
B) [option B]  
C) [option C]
D) [option D]
Correct Answer: [A, B, C, or D]

Make questions progressively challenging covering fundamentals, intermediate concepts, and advanced topics."""
    
    try:
        response = generate_llm_content(prompt, max_tokens=3000)
        return parse_questions(response)
    except Exception as e:
        print(f"Error generating questions: {e}")
        return []

def parse_questions(questions_text):
    """Parse the generated questions text into structured data"""
    questions = []
    question_blocks = re.split(r'Question \d+:', questions_text)[1:]  # Skip first empty element
    
    for i, question_block in enumerate(question_blocks):
        if i >= 25:  
            break
            
        lines = [line.strip() for line in question_block.strip().split('\n') if line.strip()]
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
    """Generate personalized learning plan"""
    percentage = (score / total_questions) * 100
    
    prompt = f"""Create a comprehensive learning plan for a student who scored {score}/{total_questions} ({percentage:.1f}%) on a {topic} assessment.

Weak areas identified:
{chr(10).join([f"- {item['question']}" for item in incorrect_answers[:3]])}

Please provide:
1. Knowledge assessment summary
2. Key focus areas for improvement
3. Recommended learning resources
4. 4-week study schedule
5. Practice exercises and projects

Format as structured markdown with clear sections."""
    
    try:
        response = generate_llm_content(prompt, max_tokens=2000)
        return response
    except Exception as e:
        print(f"Error generating learning plan: {e}")
        return "Unable to generate learning plan at this time."

@app.route('/start-assessment', methods=['POST'])
def start_assessment():
    """Start a new assessment session"""
    try:
        data = request.get_json()
        topic = data.get('topic')
        
        if not topic:
            return jsonify({'error': 'Topic is required'}), 400
        
        print(f"🚀 Starting assessment for topic: {topic}")
        
        user_id = None
        if current_user.is_authenticated:
            user_id = current_user.id
            print(f"👤 User ID: {user_id}")
        else:
            print(f"👤 Guest user - no authentication")
        
        # Generate questions
        print(f"⚡ Generating questions for {topic}...")
        questions = generate_questions(topic)
        
        if not questions:
            return jsonify({'error': 'Failed to generate questions'}), 500
        
        print(f"✅ Generated {len(questions)} questions")
        
        # Create session ID with user type indicator
        timestamp = int(time.time())
        random_suffix = uuid.uuid4().hex[:8]
        if user_id:
            session_id = f"assessment_user_{user_id}_{timestamp}_{random_suffix}"
        else:
            session_id = f"assessment_guest_{timestamp}_{random_suffix}"
        
        print(f"🔑 Created session ID: {session_id}")
        
        # Create session data
        session_data = {
            'session_id': session_id,
            'topic': topic,
            'user_id': user_id,
            'questions': questions,
            'current_question': 0,
            'answers': [],
            'score': 0,
            'started_at': datetime.utcnow(),
            'last_accessed': datetime.utcnow(),
            'total_questions': len(questions)
        }
        
        # Save session to persistent storage
        if not session_manager.save_session(session_id, session_data):
            print(f"❌ Failed to save session to persistent storage")
            return jsonify({'error': 'Failed to create session'}), 500
        
        print(f"💾 Session saved to persistent storage")
        print(f"📊 Assessment ready: {len(questions)} questions for {topic}")
        
        # Reduce cleanup frequency and set more reasonable session expiry
        if random.random() < 0.05:  # Only 5% chance of cleanup per request
            cleaned = session_manager.cleanup_expired_sessions(max_age_hours=24)  # 24 hours expiry
            if cleaned > 0:
                print(f"🧹 Cleaned up {cleaned} expired sessions")
        
        # Return the first question so frontend doesn't need additional call
        first_question = questions[0] if questions else None
    
        return jsonify({
            'session_id': session_id,
            'total_questions': len(questions),
            'first_question': first_question,  # Include first question for immediate display
            'topic': topic,
            'message': f'Assessment started with {len(questions)} questions'
        })
        
    except Exception as e:
        print(f"❌ Error starting assessment: {e}")
        return jsonify({'error': 'Failed to start assessment'}), 500

@app.route('/api/trends')
def get_trends():
    """Get trending topics from Google Trends with real-time data"""
    try:
        topic = request.args.get('topic', 'Tech Jobs')
        refresh = request.args.get('refresh', 'false').lower() == 'true'
        
        print(f"🔍 Trends request - Topic: {topic}, Refresh: {refresh}")
        
        if not refresh:
            try:
                cached_trends = TrendData.query.filter_by(topic=topic).first()
                if cached_trends and not cached_trends.is_expired():
                    print(f"✅ Using cached trends for: {topic}")
                    return jsonify({
                        'trends': cached_trends.get_trend_data(),
                        'source': 'cache',
                        'updated_at': cached_trends.created_at.isoformat()
                    })
            except Exception as e:
                print(f"⚠️ Cache check failed: {e}")
        
        print(f"🌐 Fetching FRESH data from Google Trends for: {topic}")
        
        trends = []
        try:
            pytrends = TrendReq(hl='en-US', tz=360, timeout=(10, 25), retries=2, backoff_factor=0.1)
            
            search_terms = [topic]
            if 'tech' in topic.lower() or 'software' in topic.lower():
                search_terms.extend(['Python jobs', 'JavaScript careers', 'Data Science', 'AI Engineer'])
            elif 'data' in topic.lower():
                search_terms.extend(['Machine Learning', 'Data Analyst', 'SQL', 'Analytics'])
            else:
                search_terms.extend(['Programming jobs', 'Tech careers', 'Remote work'])
            
            timeframes = ['today 1-m', 'today 3-m', 'today 12-m']
            
            for timeframe in timeframes:
                try:
                    pytrends.build_payload(search_terms[:5], cat=0, timeframe=timeframe, geo='US', gprop='')
                    
                    related_queries = pytrends.related_queries()
                    
                    for term in search_terms[:3]: 
                        if term in related_queries and related_queries[term]['top'] is not None:
                            top_queries = related_queries[term]['top']['query'].head(8).tolist()
                            for query in top_queries:
                                if query not in trends and len(query) > 3:
                                    trends.append(query)
                    
                    for term in search_terms[:2]:
                        if (term in related_queries and 
                            related_queries[term]['rising'] is not None and 
                            len(related_queries[term]['rising']) > 0):
                            rising_queries = related_queries[term]['rising']['query'].head(5).tolist()
                            for query in rising_queries:
                                if query not in trends and len(query) > 3:
                                    trends.append(f"{query} (Rising)")
                    
                    if len(trends) >= 5:
                        break
                        
                except Exception as e:
                    print(f"⚠️ Error with timeframe {timeframe}: {e}")
                    continue
            
            try:
                daily_trends = pytrends.trending_searches(pn='united_states')
                if daily_trends is not None and len(daily_trends) > 0:
                    daily_list = daily_trends[0].tolist()[:3]  # Top 3 daily trends
                    for trend in daily_list:
                        if trend not in trends and any(keyword in trend.lower() for keyword in ['tech', 'job', 'career', 'work', 'software', 'data', 'ai', 'programming']):
                            trends.append(f"{trend} (Daily Trend)")
                            
            except Exception as e:
                print(f"⚠️ Error getting daily trends: {e}")
            
            print(f"✅ Fetched {len(trends)} trends from Google")
            
        except Exception as e:
            print(f"❌ PyTrends error: {e}")
            import traceback
            traceback.print_exc()
        
        current_hour = datetime.utcnow().hour
        fallback_pools = {
            'morning': [
                'Remote software engineer jobs 2025',
                'AI developer morning shifts',
                'Data scientist work from home',
                'Cloud architect remote positions',
                'Frontend developer freelance'
            ],
            'afternoon': [
                'Full stack developer careers',
                'Machine learning engineer trends',
                'DevOps engineer job market',
                'Product manager tech roles',
                'UX designer remote work'
            ],
            'evening': [
                'Cybersecurity analyst jobs',
                'Mobile app developer careers',
                'Blockchain engineer positions',
                'Game developer opportunities',
                'Tech lead remote roles'
            ]
        }
        
        time_period = 'morning' if current_hour < 12 else 'afternoon' if current_hour < 18 else 'evening'
        fallback_trends = fallback_pools[time_period].copy()
        
        universal_trends = [
            f'Python programming jobs {datetime.utcnow().year}',
            f'React developer salary {datetime.utcnow().year}',
            'ChatGPT integration developer',
            'Kubernetes engineer demand',
            'TypeScript developer trends'
        ]
        
        if len(trends) < 3:
            trends.extend(fallback_trends[:5])
        
        while len(trends) < 5 and universal_trends:
            trend = universal_trends.pop(0)
            if trend not in trends:
                trends.append(trend)
        
        trends = list(dict.fromkeys(trends))[:5]
        
        try:
            old_cache = TrendData.query.filter_by(topic=topic).first()
            if old_cache:
                db.session.delete(old_cache)
            
            cache_hours = 2 if refresh else 6
            expires_at = datetime.utcnow() + timedelta(hours=cache_hours)
            trend_cache = TrendData(
                topic=topic,
                expires_at=expires_at
            )
            trend_cache.set_trend_data(trends)
            db.session.add(trend_cache)
            db.session.commit()
            print(f"✅ Cached {len(trends)} trends for: {topic} (expires in {cache_hours}h)")
        except Exception as e:
            print(f"⚠️ Failed to cache trends: {e}")
        
        return jsonify({
            'trends': trends,
            'source': 'fresh' if refresh else 'api',
            'updated_at': datetime.utcnow().isoformat(),
            'topic': topic,
            'count': len(trends)
        })
        
    except Exception as e:
        print(f"❌ Trends API error: {e}")
        import traceback
        traceback.print_exc()
        
        current_time = datetime.utcnow()
        fallback_trends = [
            f'Software engineering trends {current_time.strftime("%B %Y")}',
            f'Tech job market {current_time.year}',
            'Remote development opportunities',
            'AI and machine learning careers',
            f'Full-stack development {current_time.strftime("%Y")}'
        ]
        
        return jsonify({
            'trends': fallback_trends,
            'source': 'fallback',
            'error': 'Google Trends temporarily unavailable',
            'updated_at': current_time.isoformat()
        })

@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    """Submit an answer and get next question or results"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        answer = data.get('answer')
        
        if not session_id or not answer:
            return jsonify({'error': 'Session ID and answer are required'}), 400
        
        print(f"✍️ Submitting answer for session: {session_id}")
        print(f"📝 User selected: {answer}")
        
        session_data = session_manager.load_session(session_id)
        if not session_data:
            print(f"❌ Session validation failed: Session {session_id} not found")
            return jsonify({'error': f'Session {session_id} not found - please restart the assessment'}), 400
        
        print(f"✅ Session loaded successfully")
        print(f"📋 Session user_id: {session_data.get('user_id')}")
        
        current_question_index = session_data['current_question']
        questions = session_data['questions']
        
        if current_question_index >= len(questions):
            return jsonify({'error': 'Assessment already completed'}), 400
        
        current_question = questions[current_question_index]
        correct_answer = current_question['correct_answer']
        is_correct = answer == correct_answer
        
        print(f"🎯 Correct answer: {correct_answer}")
        print(f"{'✅' if is_correct else '❌'} User answer: {answer} ({'Correct' if is_correct else 'Incorrect'})")
        
        answer_record = {
            'question_id': current_question['id'],
            'question': current_question['question'],
            'user_answer': answer,
            'correct_answer': correct_answer,
            'is_correct': is_correct,
            'options': current_question['options']
        }
        session_data['answers'].append(answer_record)
        
        if is_correct:
            session_data['score'] += 1
        
        session_data['current_question'] += 1
        
        if not session_manager.save_session(session_id, session_data):
            print(f"❌ Failed to save session after answer submission")
            return jsonify({'error': 'Failed to save answer'}), 500
        
        print(f"💾 Session updated: Question {session_data['current_question']}/{len(session_data['questions'])}")
        
        if session_data['current_question'] >= len(questions):
            print(f"🎉 Assessment completed!")
            print(f"📊 Final score: {session_data['score']}/{len(questions)}")
            
            final_score = session_data['score']
            total_questions = len(questions)
            percentage = (final_score / total_questions) * 100
            
            incorrect_answers = [ans for ans in session_data['answers'] if not ans['is_correct']]
            
            user_id = session_data.get('user_id')
            if user_id:
                try:
                    # Extract correct answers from questions
                    correct_answers_list = [q['correct_answer'] for q in session_data['questions']]
                    
                    # Generate learning plan
                    learning_plan = generate_learning_plan(
                        session_data['topic'], 
                        final_score, 
                        total_questions, 
                        incorrect_answers
                    )
                    
                    new_assessment = Assessment(
                        user_id=user_id,
                        session_id=session_id,
                        topic=session_data['topic'],
                        score=final_score,
                        total_questions=total_questions,
                        score_percentage=round(percentage, 1),
                        is_completed=True,
                        completed_at=datetime.utcnow(),
                        questions_data=json.dumps(session_data['questions']),
                        user_answers=json.dumps(session_data['answers']),
                        correct_answers=json.dumps(correct_answers_list),
                        learning_plan=learning_plan
                    )
                    
                    db.session.add(new_assessment)
                    db.session.commit()
                    print(f"💾 Assessment saved to database for user {user_id}")
                    print(f"📊 Assessment details: {final_score}/{total_questions} ({percentage:.1f}%)")
                    print(f"🔑 Assessment ID: {new_assessment.id}")
                    
                    # Verify the assessment was saved
                    saved_assessment = Assessment.query.filter_by(user_id=user_id, session_id=session_id).first()
                    if saved_assessment:
                        print(f"✅ Assessment verification successful - ID: {saved_assessment.id}")
                    else:
                        print(f"❌ Assessment verification failed - not found in database")
                    
                    log_user_activity(user_id, 'assessment_complete', 
                                     f'Completed {session_data["topic"]} assessment: {final_score}/{total_questions}')
                except Exception as e:
                    print(f"⚠️ Error saving assessment to database: {e}")
                    import traceback
                    traceback.print_exc()
                    db.session.rollback()
            else:
                # Generate learning plan for guest users too
                learning_plan = generate_learning_plan(
                    session_data['topic'], 
                    final_score, 
                    total_questions, 
                    incorrect_answers
                )
                print(f"👤 Guest user - assessment not saved to database")
            
            return jsonify({
                'completed': True,
                'score': final_score,
                'total_questions': total_questions,
                'percentage': round(percentage, 1),
                'incorrect_answers': incorrect_answers,
                'learning_plan': learning_plan
            })
        
        next_question = questions[session_data['current_question']]
        return jsonify({
            'correct': is_correct,
            'correct_answer': correct_answer,
            'next_question': next_question,
            'question_number': session_data['current_question'] + 1,
            'total_questions': len(questions),
            'current_score': session_data['score']
        })
        
    except Exception as e:
        print(f"❌ Error submitting answer: {e}")
        return jsonify({'error': 'Failed to submit answer'}), 500

@app.route('/check-session/<session_id>')
@login_required
def check_session(session_id):
    """Debug endpoint to check session status"""
    print(f"🔍 Checking session: {session_id}")
    print(f"👤 Current user: {current_user.username} (ID: {current_user.id})")
    print(f"💾 Available sessions: {list(user_sessions.keys())}")
    
    if session_id in user_sessions:
        session_data = user_sessions[session_id]
        return jsonify({
            'exists': True,
            'user_id': session_data.get('user_id'),
            'current_question': session_data.get('current_question'),
            'total_questions': len(session_data.get('questions', [])),
            'topic': session_data.get('topic'),
            'started_at': session_data.get('started_at').isoformat() if session_data.get('started_at') else None
        })
    else:
        return jsonify({
            'exists': False,
            'available_sessions': list(user_sessions.keys())
        })

@app.route('/get-question', methods=['POST'])
def get_question():
    """Get current question from session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'error': 'Session ID required'}), 400
        
        print(f"🔍 Getting question for session: {session_id}")
        
        session_data = session_manager.load_session(session_id)
        if not session_data:
            print(f"❌ Session validation failed: Session {session_id} not found")
            return jsonify({'error': f'Session {session_id} not found - please restart the assessment'}), 400
        
        print(f"✅ Session loaded successfully")
        print(f"📋 Session user_id: {session_data.get('user_id')}")
        
        current_question_index = session_data['current_question']
        questions = session_data['questions']
        
        if current_question_index >= len(questions):
            print(f"🏁 Assessment completed")
            return jsonify({'completed': True})
        
        current_question = questions[current_question_index]
        
        print(f"📝 Question {current_question_index + 1}/{len(questions)}: {current_question['question'][:50]}...")
        
        return jsonify({
            'question': current_question,
            'question_number': current_question_index + 1,
            'total_questions': len(questions),
            'topic': session_data['topic']
        })
        
    except Exception as e:
        print(f"❌ Error getting question: {e}")
        return jsonify({'error': 'Failed to get question'}), 500

if __name__ == "__main__":
    print(f"🚀 Starting Pathfinder Pro Assessment System")
    print(f"📁 Sessions directory: {SESSIONS_DIR}")
    
    test_session_id = "test_startup_verification"
    test_data = {"test": True, "timestamp": datetime.utcnow()}
    
    if session_manager.save_session(test_session_id, test_data):
        loaded_data = session_manager.load_session(test_session_id)
        if loaded_data and loaded_data.get("test"):
            print(f"✅ Persistent session system verified - working correctly")
            session_manager.delete_session(test_session_id)
        else:
            print(f"⚠️ Session loading test failed")
    else:
        print(f"⚠️ Session saving test failed")
    
    cleaned = session_manager.cleanup_expired_sessions(max_age_hours=48)
    if cleaned > 0:
        print(f"🧹 Cleaned up {cleaned} old sessions on startup")
    
    with app.app_context():
        db.create_all()
        print("✅ Database tables verified")
    
    print(f"🌐 Server starting on http://localhost:5000")
    app.run(debug=True, host='0.0.0.0', port=5000) 