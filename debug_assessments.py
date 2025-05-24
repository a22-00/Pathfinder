import os
import sys
from dotenv import load_dotenv

load_dotenv()

sys.path.append(os.path.dirname(__file__))

os.chdir(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'project_learn_track'))

from project_learn_track.models import db, User, Assessment

from flask import Flask

app = Flask(__name__)
# Use the correct database path in the instance directory
db_path = os.path.join(os.path.dirname(__file__), 'project_learn_track', 'instance', 'pathfinder_pro.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

print(f"🗄️ Using database: {db_path}")
print(f"📁 Database exists: {os.path.exists(db_path)}")

def debug_database():
    """Debug the database to see what's wrong with assessments"""
    with app.app_context():
        print("🔍 Database Debug Report")
        print("=" * 60)
        
        users = User.query.all()
        print(f"👥 Total users: {len(users)}")
        
        for user in users:
            print(f"\n👤 User: {user.username} (ID: {user.id})")
            print(f"   Email: {user.email}")
            print(f"   Profession: {user.profession}")
            
            all_assessments = Assessment.query.filter_by(user_id=user.id).all()
            completed_assessments = Assessment.query.filter_by(user_id=user.id, is_completed=True).all()
            
            print(f"   📊 Total assessments: {len(all_assessments)}")
            print(f"   ✅ Completed assessments: {len(completed_assessments)}")
            
            for i, assessment in enumerate(all_assessments):
                print(f"   Assessment {i+1}:")
                print(f"     - Topic: {assessment.topic}")
                print(f"     - Score: {assessment.score}/{assessment.total_questions}")
                print(f"     - Percentage: {assessment.score_percentage}%")
                print(f"     - Completed: {assessment.is_completed}")
                print(f"     - Session ID: {assessment.session_id}")
                print(f"     - Created: {assessment.created_at}")
                print(f"     - Completed At: {assessment.completed_at}")
            
            try:
                stats = user.get_assessment_stats()
                print(f"   📈 Calculated stats: {stats}")
            except Exception as e:
                print(f"   ❌ Error calculating stats: {e}")
                import traceback
                traceback.print_exc()
        
        orphaned = Assessment.query.filter(~Assessment.user_id.in_([u.id for u in users])).all()
        print(f"\n🚨 Orphaned assessments (no user): {len(orphaned)}")
        
        print(f"\n🗃️ Database Table Info:")
        inspector = db.inspect(db.engine)
        tables = inspector.get_table_names()
        print(f"Tables: {tables}")
        
        if 'assessments' in tables:
            columns = inspector.get_columns('assessments')
            print(f"Assessment table columns:")
            for col in columns:
                print(f"  - {col['name']}: {col['type']}")

def create_test_assessment():
    """Create a test assessment to verify the system works"""
    with app.app_context():
        print("\n🧪 Creating Test Assessment...")
        
        user = User.query.first()
        if not user:
            print("❌ No users found - cannot create test assessment")
            return
        
        try:
            test_assessment = Assessment(
                user_id=user.id,
                session_id="debug_test_session_12345",
                topic="Debug Test Topic",
                score=8,
                total_questions=10,
                score_percentage=80.0,
                is_completed=True,
                completed_at=db.func.now(),
                questions_data='[{"id":1,"question":"Test?","options":{"A":"Yes","B":"No"},"correct_answer":"A"}]',
                user_answers='[{"question_id":1,"user_answer":"A","correct_answer":"A","is_correct":true}]',
                correct_answers='["A"]',
                learning_plan="Test learning plan"
            )
            
            db.session.add(test_assessment)
            db.session.commit()
            
            print(f"✅ Test assessment created with ID: {test_assessment.id}")
            
            saved = Assessment.query.filter_by(session_id="debug_test_session_12345").first()
            if saved:
                print(f"✅ Test assessment verified in database")
                
                stats = user.get_assessment_stats()
                print(f"📈 Updated stats: {stats}")
            else:
                print(f"❌ Test assessment not found after saving")
                
        except Exception as e:
            print(f"❌ Error creating test assessment: {e}")
            import traceback
            traceback.print_exc()
            db.session.rollback()

def cleanup_test_data():
    """Clean up test assessments"""
    with app.app_context():
        print("\n🧹 Cleaning up test data...")
        
        test_assessments = Assessment.query.filter(Assessment.session_id.like('debug_test%')).all()
        print(f"Found {len(test_assessments)} test assessments to clean up")
        
        for assessment in test_assessments:
            db.session.delete(assessment)
        
        db.session.commit()
        print("✅ Test data cleaned up")

if __name__ == "__main__":
    print("🐛 Assessment Database Debug Tool")
    print("=" * 60)
    
    debug_database()
    
    create_test_assessment()
    
    print("\n" + "=" * 60)
    
    response = input("Clean up test data? (y/n): ").lower().strip()
    if response == 'y':
        cleanup_test_data()
    
    print("\n💡 Next steps:")
    print("1. Check if any issues were found above")
    print("2. Try taking a real assessment now")
    print("3. Check the dashboard again")
    print("4. Look at server logs for any errors") 