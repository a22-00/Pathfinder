import socket
import subprocess
import sys
import os

def find_free_port():
    """Find an available port starting from 5001"""
    for port in range(5001, 5010):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.bind(('127.0.0.1', port))
                return port
        except OSError:
            continue
    return None

def kill_processes_on_port(port):
    """Kill any processes using the specified port"""
    try:
        result = subprocess.run(['lsof', '-t', f'-i:{port}'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            pids = result.stdout.strip().split('\n')
            for pid in pids:
                try:
                    subprocess.run(['kill', '-9', pid], check=True)
                    print(f"✅ Killed process {pid} on port {port}")
                except subprocess.CalledProcessError:
                    print(f"❌ Failed to kill process {pid}")
        else:
            print(f"ℹ️ No processes found on port {port}")
    except FileNotFoundError:
        print("ℹ️ lsof command not found, skipping process cleanup")

def main():
    print("🚀 Starting Pathfinder Application...")
    
    print("🧹 Cleaning up any existing processes on port 5001...")
    kill_processes_on_port(5001)
    
    port = find_free_port()
    if not port:
        print("❌ No available ports found in range 5001-5009")
        return 1
    
    print(f"✅ Using port {port}")
    
    os.environ['SERVER_PORT'] = str(port)
    
    try:
        print(f"🌐 Starting server on http://localhost:{port}")
        print("🛑 Press Ctrl+C to stop the server")
        print("-" * 50)
        
        subprocess.run([sys.executable, 'start_production.py'], 
                      env={**os.environ, 'SERVER_PORT': str(port)})
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
        return 0
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return 1

if __name__ == "__main__":
    exit(main()) 