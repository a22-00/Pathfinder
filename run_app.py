import os
import sys

def main():
    print("🚀 Pathfinder Pro - Fixed Startup")
    print("=" * 40)
    
    os.environ['FLASK_SECRET_KEY'] = 'dev_secret_key_123'
    os.environ['DATABASE_URL'] = 'sqlite:///pathfinder_pro.db'
    os.environ['FLASK_ENV'] = 'development'
    os.environ['FLASK_DEBUG'] = 'True'
    
    if not os.path.exists('.env'):
        with open('.env', 'w') as f:
            f.write("""FLASK_SECRET_KEY=dev_secret_key_123
DATABASE_URL=sqlite:///pathfinder_pro.db
FLASK_ENV=development
FLASK_DEBUG=True
""")
        print("📝 Created .env file")
    
    project_dir = os.path.join(os.getcwd(), 'project_learn_track')
    os.chdir(project_dir)
    
    sys.path.insert(0, os.getcwd())
    
    print("🔧 Importing Flask app...")
    
    try:
        from job_seeker import app
        
        print("\n" + "="*60)
        print("🌟 PATHFINDER PRO IS STARTING!")
        print("📱 Open: http://localhost:5000")
        print("🏠 Home: http://localhost:5000/")
        print("🔐 Login: http://localhost:5000/auth/login")
        print("📝 Register: http://localhost:5000/auth/register")
        print("🛑 Press Ctrl+C to stop")
        print("="*60)
        
        app.run(debug=True, host='0.0.0.0', port=5000)
        
    except Exception as e:
        print(f"❌ Error starting app: {e}")
        print("\n🔧 Try this manual command:")
        print("cd project_learn_track && python job_seeker.py")

if __name__ == "__main__":
    main() 