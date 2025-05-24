import os
import sys
from dotenv import load_dotenv

load_dotenv()

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

def main():
    try:
        print("🚀 Starting Pathfinder Pro application...")
        print("📁 Project directory:", project_dir)
        
        from project_learn_track.job_seeker import app
        
        print("✅ Flask app imported successfully!")
        print("🌐 Starting development server...")
        print("📍 Access the application at: http://localhost:5000")
        print("🔧 Debug mode: ON")
        print("\n" + "="*50)
        
        app.run(
            debug=True,
            host='0.0.0.0',
            port=5000,
            use_reloader=True
        )
        
    except ImportError as e:
        print(f"❌ Import Error: {e}")
        print("💡 Make sure all dependencies are installed:")
        print("   pip install flask flask-login flask-sqlalchemy flask-wtf wtforms python-dotenv anthropic pytrends pandas")
        sys.exit(1)
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main() 