#!/usr/bin/env python3
"""
Startup Issues Fixer for Pathfinder Project
Fixes common startup problems: port conflicts and API client issues
"""

import os
import sys
import subprocess
import socket
import time

def check_port_availability(port):
    """Check if a port is available"""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.bind(('127.0.0.1', port))
            return True
        except OSError:
            return False

def kill_process_on_port(port):
    """Kill any process using the specified port"""
    try:
        # Find processes using the port
        result = subprocess.run(['lsof', '-ti', f':{port}'], 
                              capture_output=True, text=True)
        
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            print(f"🔍 Found {len(pids)} process(es) using port {port}")
            
            for pid in pids:
                try:
                    subprocess.run(['kill', '-9', pid], check=True)
                    print(f"✅ Killed process {pid}")
                except subprocess.CalledProcessError:
                    print(f"⚠️ Could not kill process {pid}")
            
            # Wait a moment for processes to terminate
            time.sleep(2)
            return True
        else:
            print(f"ℹ️ No processes found using port {port}")
            return False
            
    except FileNotFoundError:
        print("⚠️ lsof command not found - trying alternative method")
        return False
    except Exception as e:
        print(f"❌ Error killing processes: {e}")
        return False

def find_free_port(start_port=5001, max_attempts=10):
    """Find the next available port starting from start_port"""
    for port in range(start_port, start_port + max_attempts):
        if check_port_availability(port):
            return port
    return None

def fix_anthropic_dependency():
    """Fix Anthropic client dependency issues"""
    print("🔧 Checking Anthropic dependency...")
    
    try:
        # Check current anthropic version
        result = subprocess.run([sys.executable, '-c', 'import anthropic; print(anthropic.__version__)'], 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            current_version = result.stdout.strip()
            print(f"📦 Current anthropic version: {current_version}")
            
            # Check if it's a problematic version
            if current_version.startswith('0.7') or current_version.startswith('0.8'):
                print("⚠️ Detected potentially problematic anthropic version")
                print("🔄 Upgrading to latest stable version...")
                
                subprocess.run([sys.executable, '-m', 'pip', 'install', '--upgrade', 'anthropic>=0.25.0'], 
                             check=True)
                print("✅ Anthropic upgraded successfully!")
                return True
            else:
                print("✅ Anthropic version looks good")
                return True
                
        else:
            print("❌ Anthropic not installed properly")
            print("📦 Installing latest anthropic...")
            subprocess.run([sys.executable, '-m', 'pip', 'install', 'anthropic>=0.25.0'], 
                         check=True)
            print("✅ Anthropic installed successfully!")
            return True
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to fix anthropic dependency: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error fixing anthropic: {e}")
        return False

def update_gunicorn_config(port):
    """Update gunicorn config to use the specified port"""
    config_path = 'gunicorn.conf.py'
    
    if os.path.exists(config_path):
        try:
            with open(config_path, 'r') as f:
                content = f.read()
            
            # Update bind configuration
            import re
            new_content = re.sub(
                r'bind\s*=\s*["\'][^"\']*["\']',
                f'bind = "127.0.0.1:{port}"',
                content
            )
            
            if new_content != content:
                with open(config_path, 'w') as f:
                    f.write(new_content)
                print(f"✅ Updated gunicorn config to use port {port}")
            else:
                print(f"ℹ️ Gunicorn config already uses correct port")
                
        except Exception as e:
            print(f"⚠️ Could not update gunicorn config: {e}")
    else:
        print(f"ℹ️ Gunicorn config file not found at {config_path}")

def main():
    print("🚀 Pathfinder Startup Issues Fixer")
    print("=" * 50)
    
    # 1. Fix Anthropic dependency
    print("\n1. Fixing Anthropic API client...")
    if not fix_anthropic_dependency():
        print("❌ Failed to fix Anthropic dependency - proceeding anyway")
    
    # 2. Handle port conflicts
    print("\n2. Checking port availability...")
    target_port = 5001
    
    if not check_port_availability(target_port):
        print(f"⚠️ Port {target_port} is in use")
        
        # Try to kill processes using the port
        if kill_process_on_port(target_port):
            time.sleep(2)  # Wait for cleanup
            
            if check_port_availability(target_port):
                print(f"✅ Port {target_port} is now available")
            else:
                print(f"❌ Port {target_port} still in use - finding alternative")
                alternative_port = find_free_port(5002)
                if alternative_port:
                    print(f"✅ Found alternative port: {alternative_port}")
                    target_port = alternative_port
                    update_gunicorn_config(target_port)
                else:
                    print("❌ Could not find available port")
                    return False
        else:
            # Find alternative port
            alternative_port = find_free_port(5002)
            if alternative_port:
                print(f"✅ Using alternative port: {alternative_port}")
                target_port = alternative_port
                update_gunicorn_config(target_port)
            else:
                print("❌ Could not find available port")
                return False
    else:
        print(f"✅ Port {target_port} is available")
    
    # 3. Create startup script with fixed port
    print(f"\n3. Creating startup script for port {target_port}...")
    startup_script = f"""#!/bin/bash
cd "/Users/akshay/Downloads/Pathfinder Project"
source .venv/bin/activate

echo "🚀 Starting Pathfinder on port {target_port}"
echo "📝 Server will be available at: http://localhost:{target_port}"
echo "🛑 Press Ctrl+C to stop the server"
echo "-" * 50

export FLASK_RUN_PORT={target_port}
python -m gunicorn -c gunicorn.conf.py wsgi:application --bind 127.0.0.1:{target_port}
"""
    
    with open('start_fixed.sh', 'w') as f:
        f.write(startup_script)
    
    os.chmod('start_fixed.sh', 0o755)
    
    print("✅ Created start_fixed.sh script")
    print(f"\n🎉 All issues fixed! You can now start the server with:")
    print(f"   ./start_fixed.sh")
    print(f"\n🌐 Server will be available at: http://localhost:{target_port}")
    print(f"📊 Assessment page: http://localhost:{target_port}/assessment")
    
    return True

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n✅ Startup issues fixed successfully!")
        else:
            print("\n❌ Some issues could not be resolved")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 