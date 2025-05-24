import os
import sys
import subprocess

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    os.chdir(script_dir)
    
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not detected!")
        print("Please activate your virtual environment first:")
        print("   source venv/bin/activate")
        print("   python start_app.py")
        sys.exit(1)
    
    if not os.path.exists('.env'):
        print("⚠️  .env file not found!")
        print("Please create a .env file with your OPENAI_API_KEY")
        print("Example:")
        print("   OPENAI_API_KEY=your_api_key_here")
        sys.exit(1)
    
    print("🚀 Starting Pathfinder Flask application...")
    print("📝 Open your browser to: http://localhost:5001")
    print("🛑 Press Ctrl+C to stop the server")
    
    try:
        subprocess.run([sys.executable, 'project_learn_track/job_seeker.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Pathfinder application stopped.")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error running application: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main() 