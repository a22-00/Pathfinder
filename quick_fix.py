import subprocess
import sys
import os

def main():
    print("🔧 Quick Fix - Installing Essential Dependencies")
    print("=" * 50)
    
    essential = [
        "flask==2.3.3",
        "flask-sqlalchemy==3.0.5", 
        "flask-login==0.6.3",
        "flask-wtf==1.1.1",
        "wtforms==3.0.1",
        "python-dotenv==1.0.0",
        "werkzeug==2.3.7",
        "email-validator==2.0.0",
        "bcrypt==4.0.1"
    ]
    
    for package in essential:
        try:
            print(f"📦 Installing {package}...")
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", package, "--quiet"
            ], timeout=30)
        except Exception as e:
            print(f"⚠️ Warning: {package} failed - {e}")
    
    print("\n✅ Essential dependencies installed!")
    print("\n🚀 Now starting the server...")
    
    # Create .env file
    if not os.path.exists(".env"):
        with open(".env", "w") as f:
            f.write("""FLASK_SECRET_KEY=dev_secret_key_123
DATABASE_URL=sqlite:///pathfinder_pro.db
FLASK_ENV=development
FLASK_DEBUG=True
""")
        print("📝 Created .env file")
    
    # Start the server
    try:
        os.chdir("project_learn_track")
        print("\n" + "="*60)
        print("🌟 PATHFINDER PRO STARTING")
        print("📱 Open: http://localhost:5000")
        print("🛑 Press Ctrl+C to stop")
        print("="*60)
        
        subprocess.check_call([sys.executable, "job_seeker.py"])
    except Exception as e:
        print(f"\n❌ Error: {e}")
        print("\n🔧 Manual command to try:")
        print("cd project_learn_track && python job_seeker.py")

if __name__ == "__main__":
    main() 