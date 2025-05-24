#!/usr/bin/env python3
"""
Pathfinder Pro - Clean Start Script
This script completely cleans and restarts the application.
"""

import os
import sys
import glob

def clean_database_files():
    """Remove any existing database files"""
    print("🧹 Cleaning old database files...")
    
    # Find and remove database files
    db_patterns = [
        "*.db",
        "pathfinder_pro.db",
        "project_learn_track/*.db",
        "**/*.db"
    ]
    
    for pattern in db_patterns:
        files = glob.glob(pattern, recursive=True)
        for file in files:
            try:
                os.remove(file)
                print(f"🗑️  Removed: {file}")
            except:
                pass
    
    print("✅ Database cleanup complete!")

def setup_environment():
    """Setup all environment variables"""
    print("🔧 Setting up environment...")
    
    env_vars = {
        'FLASK_SECRET_KEY': 'pathfinder_dev_secret_2024',
        'DATABASE_URL': 'sqlite:///pathfinder_pro.db',
        'FLASK_ENV': 'development',
        'FLASK_DEBUG': 'True'
    }
    
    for key, value in env_vars.items():
        os.environ[key] = value
    
    # Create .env file
    with open('.env', 'w') as f:
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
    
    print("✅ Environment setup complete!")

def start_application():
    """Start the Flask application"""
    print("🚀 Starting Pathfinder Pro...")
    
    # Change to project directory
    original_dir = os.getcwd()
    project_dir = os.path.join(original_dir, 'project_learn_track')
    os.chdir(project_dir)
    
    # Add to Python path
    sys.path.insert(0, os.getcwd())
    
    try:
        print("📦 Loading Flask application...")
        
        # Import Flask app
        from job_seeker import app
        
        print("\n" + "🌟" * 20)
        print("🎉 PATHFINDER PRO IS LIVE!")
        print("🌟" * 20)
        print(f"🏠 Home Page: http://localhost:5000/")
        print(f"🔐 Login: http://localhost:5000/auth/login")  
        print(f"📝 Register: http://localhost:5000/auth/register")
        print(f"💬 AI Chat: http://localhost:5000/chat")
        print(f"🧠 Assessment: http://localhost:5000/assessment")
        print("🌟" * 20)
        print("🛑 Press Ctrl+C to stop the server")
        print("🌟" * 20)
        
        # Start the server
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ Startup error: {e}")
        print("\n🔧 Debugging info:")
        print(f"Current directory: {os.getcwd()}")
        print(f"Python path: {sys.path[:3]}")
        
        # Try alternative startup
        print("\n🔄 Trying alternative startup method...")
        try:
            os.chdir(original_dir)
            os.system("cd project_learn_track && python job_seeker.py")
        except:
            print("❌ Alternative method also failed")
            print("\n💡 Manual commands to try:")
            print("1. cd project_learn_track")
            print("2. python job_seeker.py")

def main():
    """Main function"""
    print("🚀 PATHFINDER PRO - CLEAN START")
    print("=" * 50)
    
    # Check if we're in the right directory
    if not os.path.exists("project_learn_track"):
        print("❌ Error: Please run this from the Pathfinder Project directory")
        print(f"📁 Current directory: {os.getcwd()}")
        return
    
    # Clean start process
    clean_database_files()
    setup_environment()
    start_application()

if __name__ == "__main__":
    main() 