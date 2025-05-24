import os
import sys
from dotenv import load_dotenv

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

load_dotenv()

os.environ.setdefault('FLASK_ENV', 'production')
os.environ.setdefault('FLASK_DEBUG', 'False')

from project_learn_track.job_seeker import app

app.config.update(
    DEBUG=False,
    TESTING=False,
    SECRET_KEY=os.environ.get('FLASK_SECRET_KEY', 'production-secret-key-change-this'),
    SESSION_COOKIE_SECURE=True,
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE='Lax',
    PERMANENT_SESSION_LIFETIME=3600 
)

application = app

if __name__ == "__main__":
    print("⚠️  This is a WSGI entry point for production servers.")
    print("🔧 For development: python clean_start.py")
    print("🚀 For production: python start_production.py")
    print("🔒 Starting in production mode...")
    app.run(debug=False, host='127.0.0.1', port=5001) 