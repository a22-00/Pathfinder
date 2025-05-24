import os
import sys
import subprocess

def check_requirements():
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️  Virtual environment not detected!")
        print("Please activate your virtual environment first:")
        print("   source venv/bin/activate")
        print("   python start_production.py")
        return False
    
    if not os.path.exists('.env'):
        print("⚠️  .env file not found!")
        print("Please create a .env file with your API keys")
        print("You can use setup_env.py to help create it.")
        return False
    
    try:
        import gunicorn
        print(f"✅ Gunicorn version {gunicorn.__version__} found")
    except ImportError:
        print("❌ Gunicorn not found! Installing...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "gunicorn"])
            print("✅ Gunicorn installed successfully")
        except subprocess.CalledProcessError:
            print("❌ Failed to install Gunicorn!")
            print("Manual installation: pip install gunicorn")
            return False
    
    return True

def start_production_server():
    if not check_requirements():
        sys.exit(1)
    
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    
    print("🚀 Starting Pathfinder with Gunicorn (Production Server)")
    print("📝 Server will be available at: http://localhost:5001")
    print("🔧 Using configuration: gunicorn.conf.py")
    print("🛑 Press Ctrl+C to stop the server")
    print("-" * 50)
    
    cmd = [
        sys.executable, "-m", "gunicorn",
        "-c", "gunicorn.conf.py",
        "wsgi:application"
    ]
    
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        
        for line in iter(process.stdout.readline, ''):
            print(line.strip())
            
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping Pathfinder server...")
        process.terminate()
        process.wait()
        print("👋 Server stopped successfully.")
        
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        sys.exit(1)

if __name__ == '__main__':
    start_production_server() 