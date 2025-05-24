import os
import sys
import subprocess
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    required_packages = [
        'flask', 'flask_sqlalchemy', 'flask_login', 'flask_wtf', 
        'wtforms', 'werkzeug', 'python_dotenv', 'anthropic', 
        'pytrends', 'pandas', 'bcrypt', 'email_validator'
    ]
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            missing_packages.append(package)
    
    return missing_packages

def install_dependencies_fast():
    """Install dependencies with faster alternatives"""
    print("🔧 Installing dependencies (fast method)...")
    
    core_packages = [
        "Flask==2.3.3",
        "python-dotenv==1.0.0", 
        "Flask-SQLAlchemy==3.0.5",
        "Flask-Login==0.6.3",
        "Flask-WTF==1.1.1",
        "WTForms==3.0.1",
        "Werkzeug==2.3.7",
        "email-validator==2.0.0",
        "bcrypt==4.0.1"
    ]
    
    try:
        for package in core_packages:
            print(f"📦 Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package, "--quiet"
            ], timeout=60)
        
        optional_packages = [
            "anthropic==0.7.4",
            "pytrends==4.9.2", 
            "pandas>=1.3.0"  
        ]
        
        for package in optional_packages:
            try:
                print(f"📦 Installing {package} (optional)...")
                subprocess.check_call([
                    sys.executable, "-m", "pip", "install", package, "--quiet"
                ], timeout=120)
            except (subprocess.CalledProcessError, subprocess.TimeoutExpired):
                print(f"⚠️  Could not install {package} - app will work with fallbacks")
                continue
        
        print("✅ Core dependencies installed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False
    except subprocess.TimeoutExpired:
        print("⏰ Installation timeout - trying alternative method...")
        return False

def install_dependencies():
    """Install missing dependencies using requirements.txt"""
    print("🔧 Installing dependencies from requirements.txt...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully!")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        print("🔄 Trying alternative installation method...")
        return install_dependencies_fast()

def setup_environment():
    env_file = Path(".env")
    if not env_file.exists():
        print("📝 Creating .env file...")
        env_content = """# Pathfinder Pro Configuration
FLASK_SECRET_KEY=pathfinder_pro_secret_key_2024!@#$%^&*()
DATABASE_URL=sqlite:///pathfinder_pro.db
ANTHROPIC_API_KEY=your_anthropic_api_key_here
FLASK_ENV=development
FLASK_DEBUG=True
"""
        with open(".env", "w") as f:
            f.write(env_content)
        print("✅ .env file created! Please update ANTHROPIC_API_KEY if you have one.")

def run_server():
    print("\n🚀 Starting Pathfinder Pro server...")
    print("=" * 60)
    print("🌟 PATHFINDER PRO - AI Career Intelligence Platform")
    print("=" * 60)
    print("📊 Dashboard: http://localhost:5000/")
    print("🏠 Home Page: http://localhost:5000/")
    print("🔐 Login: http://localhost:5000/auth/login")
    print("📝 Register: http://localhost:5000/auth/register")
    print("💬 AI Chat: http://localhost:5000/chat")
    print("🧠 Assessment: http://localhost:5000/assessment")
    print("=" * 60)
    print("💡 Press Ctrl+C to stop the server")
    print("=" * 60)
    
    try:
        project_path = os.path.join(os.getcwd(), 'project_learn_track')
        if project_path not in sys.path:
            sys.path.insert(0, project_path)
        
        from project_learn_track.job_seeker import app
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except ImportError as e:
        print(f"🔧 Import error, trying alternative import: {e}")
        try:
            os.chdir('project_learn_track')
            sys.path.insert(0, os.getcwd())
            from job_seeker import app
            app.run(debug=True, host='0.0.0.0', port=5000)
        except Exception as e2:
            print(f"❌ Failed to start server: {e2}")
            print("\n🔧 Troubleshooting suggestions:")
            print("1. Make sure you're in the Pathfinder Project directory")
            print("2. Try: cd project_learn_track && python job_seeker.py")
            print("3. Check that all dependencies are installed")
            return False
    except Exception as e:
        print(f"❌ Server error: {e}")
        return False

def main():
    """Main startup function"""
    print("🚀 Pathfinder Pro Startup Script")
    print("=" * 40)
    
    if not os.path.exists("project_learn_track"):
        print("❌ Please run this script from the Pathfinder Project directory")
        print(f"📁 Current directory: {os.getcwd()}")
        return
    
    setup_environment()
    
    print("\n🔍 Checking dependencies...")
    missing = check_dependencies()
    
    if missing:
        print(f"⚠️  Missing packages: {', '.join(missing)}")
        response = input("Install missing dependencies? (y/n): ").lower().strip()
        if response in ['y', 'yes']:
            if not install_dependencies():
                print("❌ Failed to install dependencies.")
                print("🔧 Manual installation command:")
                print("pip install flask flask-sqlalchemy flask-login flask-wtf python-dotenv")
                return
        else:
            print("⚠️  Some features may not work without all dependencies.")
    else:
        print("✅ All dependencies are installed!")
    
    run_server()

if __name__ == "__main__":
    main() 