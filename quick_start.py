import os
import sys
import subprocess
import webbrowser
import time

def check_python_version():
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ required")
        sys.exit(1)
    print(f"✅ Python: {sys.version.split()[0]}")

def check_virtual_environment():
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("⚠️ Virtual environment not detected")
        choice = input("Continue anyway? (y/N): ").lower()
        if choice != 'y':
            sys.exit(1)
    else:
        print("✅ Virtual environment active")

def check_dependencies():
    print("📦 Checking dependencies...")
    required_packages = ['flask', 'anthropic', 'python-dotenv', 'pytrends', 'pandas', 'requests']
    
    missing_packages = []
    for package in required_packages:
        try:
            __import__(package.replace('-', '_'))
            print(f"  ✅ {package}")
        except ImportError:
            print(f"  ❌ {package}")
            missing_packages.append(package)
    
    if missing_packages:
        print(f"\n🔧 Installing: {', '.join(missing_packages)}")
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'install'] + missing_packages)
            print("✅ Dependencies installed")
        except subprocess.CalledProcessError:
            print("❌ Install failed")
            sys.exit(1)

def check_environment_file():
    if not os.path.exists('.env'):
        print("⚠️ Creating .env file...")
        env_content = """ANTHROPIC_API_KEY=your_key_here
FLASK_SECRET_KEY=your_secret_here"""
        
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("📝 .env created")
        print("❗ Add your ANTHROPIC_API_KEY to .env")
        input("Press Enter when done...")
    
    try:
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        print("❌ python-dotenv not installed")
        sys.exit(1)
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key or api_key == "your_key_here":
        print("❌ ANTHROPIC_API_KEY not configured")
        sys.exit(1)
    
    print(f"✅ API key configured")

def start_application():
    print("\n🚀 Starting Pathfinder AI...")
    print("📱 http://localhost:5001")
    
    def open_browser():
        time.sleep(2)
        webbrowser.open('http://localhost:5001')
    
    import threading
    browser_thread = threading.Thread(target=open_browser)
    browser_thread.daemon = True
    browser_thread.start()
    
    try:
        subprocess.run([sys.executable, 'project_learn_track/job_seeker.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e}")
        sys.exit(1)

def main():
    print("🎯 PATHFINDER AI - QUICK START")
    print("=" * 30)
    
    check_python_version()
    check_virtual_environment()
    check_dependencies()
    check_environment_file()
    
    print("\n✨ Starting...")
    start_application()

if __name__ == "__main__":
    main() 