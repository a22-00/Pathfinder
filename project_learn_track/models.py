from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import json

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    first_name = db.Column(db.String(50), nullable=True)
    last_name = db.Column(db.String(50), nullable=True)
    profession = db.Column(db.String(100), nullable=True)
    experience_level = db.Column(db.String(20), nullable=True) 
    career_goals = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True)  
    location = db.Column(db.String(100), nullable=True)
    profile_picture = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Relationships
    chat_conversations = db.relationship('ChatConversation', backref='user', lazy=True, cascade='all, delete-orphan')
    assessments = db.relationship('Assessment', backref='user', lazy=True, cascade='all, delete-orphan')
    recommendations = db.relationship('Recommendation', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        """Hash and set password"""
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        """Check if provided password matches hash"""
        return check_password_hash(self.password_hash, password)
    
    def get_skills_list(self):
        """Return skills as a list"""
        if self.skills:
            try:
                return json.loads(self.skills)
            except:
                return []
        return []
    
    def set_skills_list(self, skills_list):
        """Set skills from a list"""
        self.skills = json.dumps(skills_list)
    
    def get_full_name(self):
        """Return full name"""
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def get_assessment_stats(self):
        """Get user's assessment statistics"""
        assessments = Assessment.query.filter_by(user_id=self.id, is_completed=True).all()
        if not assessments:
            return {'total': 0, 'average_score': 0, 'highest_score': 0}
        
        scores = [a.score_percentage for a in assessments]
        return {
            'total': len(assessments),
            'average_score': round(sum(scores) / len(scores), 1),
            'highest_score': max(scores)
        }
    
    def __repr__(self):
        return f'<User {self.username}>'

class ChatConversation(db.Model):
    __tablename__ = 'chat_conversations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    title = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = db.relationship('ChatMessage', backref='conversation', lazy=True, cascade='all, delete-orphan')
    
    def get_last_message(self):
        """Get the last message in this conversation"""
        return ChatMessage.query.filter_by(conversation_id=self.id).order_by(ChatMessage.created_at.desc()).first()
    
    def get_message_count(self):
        """Get total number of messages in this conversation"""
        return ChatMessage.query.filter_by(conversation_id=self.id).count()

class ChatMessage(db.Model):
    __tablename__ = 'chat_messages'
    
    id = db.Column(db.Integer, primary_key=True)
    conversation_id = db.Column(db.Integer, db.ForeignKey('chat_conversations.id'), nullable=False)
    message_type = db.Column(db.String(10), nullable=False)  # 'user' or 'ai'
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<ChatMessage {self.message_type}: {self.content[:50]}>'

class Assessment(db.Model):
    __tablename__ = 'assessments'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    session_id = db.Column(db.String(100), unique=True, nullable=False)
    topic = db.Column(db.String(200), nullable=False)
    total_questions = db.Column(db.Integer, nullable=False)
    questions_data = db.Column(db.Text, nullable=False)  
    current_question_index = db.Column(db.Integer, default=0)
    score = db.Column(db.Integer, default=0)
    score_percentage = db.Column(db.Float, default=0.0)
    user_answers = db.Column(db.Text, nullable=True)  
    correct_answers = db.Column(db.Text, nullable=True)  
    is_completed = db.Column(db.Boolean, default=False)
    learning_plan = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    completed_at = db.Column(db.DateTime, nullable=True)
    
    def get_questions(self):
        """Return questions as a list"""
        try:
            return json.loads(self.questions_data)
        except:
            return []
    
    def set_questions(self, questions_list):
        """Set questions from a list"""
        self.questions_data = json.dumps(questions_list)
    
    def get_user_answers(self):
        """Return user answers as a list"""
        if self.user_answers:
            try:
                return json.loads(self.user_answers)
            except:
                return []
        return []
    
    def set_user_answers(self, answers_list):
        """Set user answers from a list"""
        self.user_answers = json.dumps(answers_list)
    
    def get_correct_answers(self):
        """Return correct answers as a list"""
        if self.correct_answers:
            try:
                return json.loads(self.correct_answers)
            except:
                return []
        return []
    
    def set_correct_answers(self, answers_list):
        """Set correct answers from a list"""
        self.correct_answers = json.dumps(answers_list)
    
    def get_current_question(self):
        """Get the current question"""
        questions = self.get_questions()
        if self.current_question_index < len(questions):
            return questions[self.current_question_index]
        return None
    
    def add_answer(self, answer):
        """Add an answer and move to next question"""
        answers = self.get_user_answers()
        answers.append(answer)
        self.set_user_answers(answers)
        self.current_question_index += 1
    
    def calculate_score(self):
        """Calculate the final score"""
        user_answers = self.get_user_answers()
        correct_answers = self.get_correct_answers()
        
        if not user_answers or not correct_answers:
            return 0, 0.0
        
        correct_count = sum(1 for i, answer in enumerate(user_answers) 
                          if i < len(correct_answers) and answer == correct_answers[i])
        
        percentage = (correct_count / len(correct_answers)) * 100 if correct_answers else 0
        
        self.score = correct_count
        self.score_percentage = round(percentage, 1)
        
        return correct_count, percentage

class Recommendation(db.Model):
    __tablename__ = 'recommendations'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    type = db.Column(db.String(50), nullable=False)  
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    url = db.Column(db.String(500), nullable=True)
    priority = db.Column(db.Integer, default=1)  
    is_completed = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<Recommendation {self.title}>'

class UserActivity(db.Model):
    __tablename__ = 'user_activities'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    activity_type = db.Column(db.String(50), nullable=False) 
    description = db.Column(db.String(200), nullable=True)
    activity_metadata = db.Column(db.Text, nullable=True) 
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship
    user = db.relationship('User', backref='activities')
    
    def get_metadata(self):
        """Return metadata as a dict"""
        if self.activity_metadata:
            try:
                return json.loads(self.activity_metadata)
            except:
                return {}
        return {}
    
    def set_metadata(self, metadata_dict):
        """Set metadata from a dict"""
        self.activity_metadata = json.dumps(metadata_dict)

class TrendData(db.Model):
    __tablename__ = 'trend_data'
    
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String(100), nullable=False)
    trend_data = db.Column(db.Text, nullable=False)  
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    expires_at = db.Column(db.DateTime, nullable=False)  
    
    def get_trend_data(self):
        """Return trend data as a list"""
        try:
            return json.loads(self.trend_data)
        except:
            return []
    
    def set_trend_data(self, data_list):
        """Set trend data from a list"""
        self.trend_data = json.dumps(data_list)
    
    def is_expired(self):
        """Check if trend data is expired"""
        return datetime.utcnow() > self.expires_at

# Helper functions for database operations
def create_user(username, email, password, **kwargs):
    """Create a new user"""
    user = User(username=username, email=email, **kwargs)
    user.set_password(password)
    db.session.add(user)
    db.session.commit()
    return user

def log_user_activity(user_id, activity_type, description=None, metadata=None):
    """Log user activity"""
    activity = UserActivity(
        user_id=user_id,
        activity_type=activity_type,
        description=description
    )
    if metadata:
        activity.set_metadata(metadata)
    
    db.session.add(activity)
    db.session.commit()
    return activity

def get_user_recommendations(user_id, limit=10):
    """Get recommendations for a user"""
    return Recommendation.query.filter_by(user_id=user_id, is_completed=False)\
                              .order_by(Recommendation.priority.asc(), Recommendation.created_at.desc())\
                              .limit(limit).all()

def create_chat_conversation(user_id, title=None):
    """Create a new chat conversation"""
    conversation = ChatConversation(user_id=user_id, title=title)
    db.session.add(conversation)
    db.session.commit()
    return conversation

def add_chat_message(conversation_id, message_type, content):
    """Add a message to a conversation"""
    message = ChatMessage(
        conversation_id=conversation_id,
        message_type=message_type,
        content=content
    )
    db.session.add(message)
    db.session.commit()
    return message 