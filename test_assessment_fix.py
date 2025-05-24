#!/usr/bin/env python3
"""
Test script to verify assessment saving functionality
"""

import os
import sys
sys.path.append(os.path.dirname(__file__))

from project_learn_track import db
from project_learn_track.models import User, Assessment
from datetime import datetime
import json

def test_assessment_creation():
    """Test creating an assessment with all required fields"""
    print("🧪 Testing Assessment Creation...")
    
    # Test data
    test_user_id = 1  # Adjust based on your user
    test_session_id = "test_session_123"
    test_topic = "Python Programming"
    test_score = 8
    test_total = 10
    test_percentage = 80.0
    
    test_questions = [
        {"id": 1, "question": "What is Python?", "options": {"A": "Language", "B": "Snake"}, "correct_answer": "A"},
        {"id": 2, "question": "What is a list?", "options": {"A": "Data structure", "B": "Animal"}, "correct_answer": "A"}
    ]
    
    test_answers = [
        {"question_id": 1, "user_answer": "A", "correct_answer": "A", "is_correct": True},
        {"question_id": 2, "user_answer": "B", "correct_answer": "A", "is_correct": False}
    ]
    
    try:
        # Create assessment with all fields
        new_assessment = Assessment(
            user_id=test_user_id,
            session_id=test_session_id,
            topic=test_topic,
            score=test_score,
            total_questions=test_total,
            score_percentage=test_percentage,
            results=json.dumps(test_answers),
            is_completed=True,
            completed_at=datetime.utcnow(),
            questions_data=json.dumps(test_questions)
        )
        
        new_assessment.user_answers = json.dumps(test_answers)
        
        print(f"✅ Assessment object created successfully")
        print(f"📊 Topic: {new_assessment.topic}")
        print(f"📊 Score: {new_assessment.score}/{new_assessment.total_questions}")
        print(f"📊 Percentage: {new_assessment.score_percentage}%")
        print(f"📊 Completed: {new_assessment.is_completed}")
        print(f"📊 User ID: {new_assessment.user_id}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating assessment: {e}")
        return False

def test_user_stats():
    """Test user stats calculation"""
    print("\n🧪 Testing User Stats...")
    
    try:
        # Try to get a user
        user = User.query.first()
        if not user:
            print("❌ No users found in database")
            return False
            
        print(f"👤 Testing with user: {user.username} (ID: {user.id})")
        
        # Get stats
        stats = user.get_assessment_stats()
        print(f"📈 Stats: {stats}")
        
        # Get assessments
        assessments = Assessment.query.filter_by(user_id=user.id, is_completed=True).all()
        print(f"📊 Found {len(assessments)} completed assessments")
        
        for assessment in assessments:
            print(f"  - {assessment.topic}: {assessment.score}/{assessment.total_questions} ({assessment.score_percentage}%)")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing user stats: {e}")
        return False

if __name__ == "__main__":
    print("🔧 Assessment Fix Test Script")
    print("=" * 50)
    
    # Test 1: Assessment creation
    test1_result = test_assessment_creation()
    
    # Test 2: User stats
    test2_result = test_user_stats()
    
    print("\n" + "=" * 50)
    if test1_result and test2_result:
        print("✅ All tests passed!")
    else:
        print("❌ Some tests failed. Check the output above.")
    
    print("\n💡 Next steps:")
    print("1. Take a new assessment to test the fix")
    print("2. Check your dashboard to see if stats update")
    print("3. Look for the debug output in the server logs") 