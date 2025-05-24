import os
import sys
import subprocess

def install_essential_deps():
    """Install only the most essential dependencies"""
    essential_packages = [
        "flask",
        "flask-sqlalchemy", 
        "flask-login",
        "flask-wtf",
        "python-dotenv"
    ]
    
    print("🔧 Installing essential dependencies...")
    for package in essential_packages:
        try:
            print(f"📦 Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package
            ], stdout=subprocess.DEVNULL)
        except subprocess.CalledProcessError:
            print(f"⚠️  Could not install {package}")
    
    print("✅ Essential dependencies installed!")

def run_app():
    """Run the application"""
    print("\n🚀 Starting Pathfinder Pro...")
    
    # Set environment variables
    os.environ['FLASK_SECRET_KEY'] = 'dev_secret_key_123'
    os.environ['DATABASE_URL'] = 'sqlite:///pathfinder_pro.db'
    
    try:
        # Change to project directory and run
        os.chdir('project_learn_track')
        
        # Run the app directly
        subprocess.check_call([sys.executable, "job_seeker.py"])
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("\n🔧 Alternative command to try:")
        print("cd project_learn_track && python job_seeker.py")

if __name__ == "__main__":
    print("🚀 Pathfinder Pro - Simple Start")
    print("=" * 40)
    
    if not os.path.exists("project_learn_track"):
        print("❌ Run this from the Pathfinder Project directory")
        sys.exit(1)
    
    install_essential_deps()
    run_app() 