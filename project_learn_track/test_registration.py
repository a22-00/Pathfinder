import os
import sys
sys.path.append(os.path.dirname(__file__))

from models import db, User, create_user
from forms import RegistrationForm
from flask import Flask

app = Flask(__name__)
app.secret_key = "test_secret_key"
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test_pathfinder.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['WTF_CSRF_ENABLED'] = False

db.init_app(app)

def test_registration():
    with app.app_context():
        # Create tables
        db.create_all()
        
        print("🧪 Testing Registration Functionality")
        print("=" * 50)
        
        try:
            test_user = User(username="testuser", email="test@example.com")
            test_user.set_password("testpassword123")
            print("✅ User model creation: PASSED")
        except Exception as e:
            print(f"❌ User model creation: FAILED - {e}")
            return
        
        try:
            user = create_user(
                username="testuser2",
                email="test2@example.com", 
                password="testpassword123",
                first_name="Test",
                last_name="User"
            )
            print("✅ create_user function: PASSED")
            print(f"   Created user: {user.username} ({user.email})")
        except Exception as e:
            print(f"❌ create_user function: FAILED - {e}")
            return
        
        try:
            form = RegistrationForm()
            print("✅ RegistrationForm import: PASSED")
        except Exception as e:
            print(f"❌ RegistrationForm import: FAILED - {e}")
            return
        
        try:
            users = User.query.all()
            print(f"✅ Database query: PASSED - Found {len(users)} users")
        except Exception as e:
            print(f"❌ Database query: FAILED - {e}")
            return
        
        print("\n🎉 All tests passed! Registration should work properly.")
        print("\nPossible issues to check:")
        print("1. Form validation errors (check browser console)")
        print("2. CSRF token issues")
        print("3. Database permissions")
        print("4. Flask session configuration")

if __name__ == "__main__":
    test_registration() 