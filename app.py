import os
import sys
from dotenv import load_dotenv

# project directory
project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

load_dotenv()

from project_learn_track.job_seeker import app

if __name__ == "__main__":
    print("⚠️  This is the production entry point.")
    print("For development, use: python start_app.py")
    print("For production, use: gunicorn app:app")
    app.run(debug=False, host='0.0.0.0', port=5001) 