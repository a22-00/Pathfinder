import json
import os
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
import hashlib

class UserProfile:
    def __init__(self, user_id: str = None):
        self.user_id = user_id or str(uuid.uuid4())
        self.created_at = datetime.now().isoformat()
        self.last_active = datetime.now().isoformat()
        
        # Basic profile info
        self.name = ""
        self.experience_level = "" 
        self.current_role = ""
        self.target_industry = ""
        self.target_role = ""
        self.location = ""
        
        # Skills and interests
        self.skills = []
        self.interests = []
        self.strengths = []
        self.areas_to_improve = []
        
        # Preferences
        self.communication_style = "professional"  
        self.learning_pace = "moderate" 
        self.preferred_content_types = ["articles", "videos", "exercises"]
        
        # Progress tracking
        self.completed_topics = []
        self.learning_goals = []
        self.interview_history = []
        self.skill_assessments = {}
        
        self.conversation_count = 0
        self.total_time_spent = 0
        self.preferred_session_length = "medium"  
        self.most_active_times = []

    def to_dict(self) -> Dict:
        return {
            'user_id': self.user_id,
            'created_at': self.created_at,
            'last_active': self.last_active,
            'name': self.name,
            'experience_level': self.experience_level,
            'current_role': self.current_role,
            'target_industry': self.target_industry,
            'target_role': self.target_role,
            'location': self.location,
            'skills': self.skills,
            'interests': self.interests,
            'strengths': self.strengths,
            'areas_to_improve': self.areas_to_improve,
            'communication_style': self.communication_style,
            'learning_pace': self.learning_pace,
            'preferred_content_types': self.preferred_content_types,
            'completed_topics': self.completed_topics,
            'learning_goals': self.learning_goals,
            'interview_history': self.interview_history,
            'skill_assessments': self.skill_assessments,
            'conversation_count': self.conversation_count,
            'total_time_spent': self.total_time_spent,
            'preferred_session_length': self.preferred_session_length,
            'most_active_times': self.most_active_times
        }

    @classmethod
    def from_dict(cls, data: Dict) -> 'UserProfile':
        profile = cls(data.get('user_id'))
        for key, value in data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)
        return profile

class ConversationMemory:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.conversations = []
        self.context_summary = ""
        self.key_topics = []
        self.sentiment_history = []

    def add_conversation(self, user_message: str, ai_response: str, topic: str = "general"):
        conversation = {
            'timestamp': datetime.now().isoformat(),
            'user_message': user_message,
            'ai_response': ai_response,
            'topic': topic,
            'message_length': len(user_message),
            'response_length': len(ai_response)
        }
        self.conversations.append(conversation)
        
        if len(self.conversations) > 50:
            self.conversations = self.conversations[-50:]
        
        self._update_context_summary()

    def _update_context_summary(self):
        recent_conversations = self.conversations[-5:]
        topics = [conv['topic'] for conv in recent_conversations]
        self.key_topics = list(set(topics))
        
        if recent_conversations:
            self.context_summary = f"Recent focus: {', '.join(self.key_topics)}"

    def get_relevant_context(self, current_topic: str, limit: int = 3) -> List[Dict]:
        relevant = [conv for conv in self.conversations if conv['topic'] == current_topic]
        return relevant[-limit:] if relevant else self.conversations[-limit:]

class PersonalizationEngine:
    def __init__(self, data_dir: str = "user_data"):
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        self.user_profiles = {}
        self.conversation_memories = {}

    def get_user_id_from_session(self, session_data: Dict) -> str:
        session_str = json.dumps(session_data, sort_keys=True)
        return hashlib.md5(session_str.encode()).hexdigest()[:12]

    def get_or_create_profile(self, user_id: str) -> UserProfile:
        if user_id not in self.user_profiles:
            profile_path = os.path.join(self.data_dir, f"profile_{user_id}.json")
            if os.path.exists(profile_path):
                with open(profile_path, 'r') as f:
                    data = json.load(f)
                    self.user_profiles[user_id] = UserProfile.from_dict(data)
            else:
                self.user_profiles[user_id] = UserProfile(user_id)
        
        return self.user_profiles[user_id]

    def save_profile(self, user_id: str):
        if user_id in self.user_profiles:
            profile_path = os.path.join(self.data_dir, f"profile_{user_id}.json")
            with open(profile_path, 'w') as f:
                json.dump(self.user_profiles[user_id].to_dict(), f, indent=2)

    def get_conversation_memory(self, user_id: str) -> ConversationMemory:
        if user_id not in self.conversation_memories:
            memory_path = os.path.join(self.data_dir, f"memory_{user_id}.json")
            memory = ConversationMemory(user_id)
            if os.path.exists(memory_path):
                with open(memory_path, 'r') as f:
                    data = json.load(f)
                    memory.conversations = data.get('conversations', [])
                    memory.context_summary = data.get('context_summary', "")
                    memory.key_topics = data.get('key_topics', [])
            self.conversation_memories[user_id] = memory
        
        return self.conversation_memories[user_id]

    def save_conversation_memory(self, user_id: str):
        if user_id in self.conversation_memories:
            memory_path = os.path.join(self.data_dir, f"memory_{user_id}.json")
            memory = self.conversation_memories[user_id]
            data = {
                'conversations': memory.conversations,
                'context_summary': memory.context_summary,
                'key_topics': memory.key_topics
            }
            with open(memory_path, 'w') as f:
                json.dump(data, f, indent=2)

    def update_user_preferences(self, user_id: str, preferences: Dict):
        profile = self.get_or_create_profile(user_id)
        
        if 'experience_level' in preferences:
            profile.experience_level = preferences['experience_level']
        if 'target_industry' in preferences:
            profile.target_industry = preferences['target_industry']
        if 'target_role' in preferences:
            profile.target_role = preferences['target_role']
        if 'communication_style' in preferences:
            profile.communication_style = preferences['communication_style']
        
        profile.last_active = datetime.now().isoformat()
        self.save_profile(user_id)

    def learn_from_interaction(self, user_id: str, user_message: str, ai_response: str, topic: str = "general"):
        memory = self.get_conversation_memory(user_id)
        memory.add_conversation(user_message, ai_response, topic)
        self.save_conversation_memory(user_id)
        
        profile = self.get_or_create_profile(user_id)
        profile.conversation_count += 1
        profile.last_active = datetime.now().isoformat()
        
        if len(user_message) > 200:
            profile.preferred_session_length = "long"
        elif len(user_message) < 50:
            profile.preferred_session_length = "short"
        
        self._extract_skills_from_message(profile, user_message)
        
        self.save_profile(user_id)

    def _extract_skills_from_message(self, profile: UserProfile, message: str):
        common_skills = [
            'python', 'javascript', 'react', 'node.js', 'sql', 'aws', 'docker',
            'machine learning', 'data analysis', 'project management', 'leadership',
            'communication', 'problem solving', 'teamwork', 'agile', 'scrum'
        ]
        
        message_lower = message.lower()
        for skill in common_skills:
            if skill in message_lower and skill not in profile.skills:
                profile.skills.append(skill)

    def get_personalized_prompt(self, user_id: str, base_prompt: str) -> str:
        profile = self.get_or_create_profile(user_id)
        memory = self.get_conversation_memory(user_id)
        
        personalization_context = []
        
        if profile.experience_level:
            personalization_context.append(f"User experience level: {profile.experience_level}")
        
        if profile.target_industry:
            personalization_context.append(f"Target industry: {profile.target_industry}")
        
        if profile.target_role:
            personalization_context.append(f"Target role: {profile.target_role}")
        
        if profile.communication_style:
            style_map = {
                "casual": "Use a friendly, conversational tone",
                "professional": "Use a professional, business-appropriate tone",
                "technical": "Use technical language and detailed explanations"
            }
            personalization_context.append(style_map.get(profile.communication_style, ""))
        
        if profile.skills:
            personalization_context.append(f"Known skills: {', '.join(profile.skills[:5])}")
        
        if memory.context_summary:
            personalization_context.append(f"Conversation context: {memory.context_summary}")
        
        recent_context = memory.get_relevant_context("general", 2)
        if recent_context:
            recent_topics = [conv['topic'] for conv in recent_context]
            personalization_context.append(f"Recent topics discussed: {', '.join(recent_topics)}")
        
        if personalization_context:
            personalized_prompt = f"""
PERSONALIZATION CONTEXT:
{chr(10).join('- ' + ctx for ctx in personalization_context)}

USER REQUEST:
{base_prompt}

Please provide a response that takes into account the user's background and preferences mentioned above.
"""
        else:
            personalized_prompt = base_prompt
        
        return personalized_prompt

    def get_recommendations(self, user_id: str) -> List[Dict]:
        profile = self.get_or_create_profile(user_id)
        memory = self.get_conversation_memory(user_id)
        
        recommendations = []
        
        # Skill based recommendations
        if profile.target_role and not profile.skills:
            recommendations.append({
                'type': 'skill_assessment',
                'title': 'Complete Skills Assessment',
                'description': f'Help us understand your current skills for {profile.target_role}',
                'priority': 'high'
            })
        
        # Industry-specific recommendations
        if profile.target_industry:
            recommendations.append({
                'type': 'industry_trends',
                'title': f'Latest {profile.target_industry} Trends',
                'description': f'Stay updated with current trends in {profile.target_industry}',
                'priority': 'medium'
            })
        
        # Experience based recommendations
        if profile.experience_level == 'entry':
            recommendations.append({
                'type': 'basic_interview_prep',
                'title': 'Interview Basics',
                'description': 'Learn fundamental interview techniques and common questions',
                'priority': 'high'
            })
        
        return recommendations

personalization_engine = PersonalizationEngine() 