#!/usr/bin/env python3
"""
Server Shutdown Script for Pathfinder Project
Safely stops all server processes
"""

import os
import sys
import subprocess
import signal
import time

def find_pathfinder_processes():
    """Find all Pathfinder-related processes"""
    processes = []
    
    try:
        # Find gunicorn processes
        result = subprocess.run(['pgrep', '-f', 'gunicorn.*wsgi:application'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            gunicorn_pids = result.stdout.strip().split('\n')
            processes.extend([(pid, 'gunicorn') for pid in gunicorn_pids])
        
        # Find python processes running our app
        result = subprocess.run(['pgrep', '-f', 'python.*start_production.py'], 
                              capture_output=True, text=True)
        if result.stdout.strip():
            python_pids = result.stdout.strip().split('\n')
            processes.extend([(pid, 'python') for pid in python_pids])
        
        # Find processes using ports 5001-5010 (our typical range)
        for port in range(5001, 5011):
            result = subprocess.run(['lsof', '-ti', f':{port}'], 
                                  capture_output=True, text=True)
            if result.stdout.strip():
                port_pids = result.stdout.strip().split('\n')
                processes.extend([(pid, f'port-{port}') for pid in port_pids])
        
    except FileNotFoundError:
        print("⚠️ Some system commands not found, using alternative method...")
        return []
    except Exception as e:
        print(f"❌ Error finding processes: {e}")
        return []
    
    # Remove duplicates
    unique_processes = list(set(processes))
    return unique_processes

def stop_process(pid, process_type, graceful=True):
    """Stop a process gracefully or forcefully"""
    try:
        pid_int = int(pid)
        
        if graceful:
            # Try graceful shutdown first (SIGTERM)
            os.kill(pid_int, signal.SIGTERM)
            print(f"📤 Sent SIGTERM to {process_type} process {pid}")
            
            # Wait a bit for graceful shutdown
            for _ in range(5):
                try:
                    os.kill(pid_int, 0)  # Check if process still exists
                    time.sleep(1)
                except OSError:
                    print(f"✅ Process {pid} stopped gracefully")
                    return True
            
            print(f"⚠️ Process {pid} didn't respond to SIGTERM, trying SIGKILL...")
        
        # Force kill if graceful didn't work
        os.kill(pid_int, signal.SIGKILL)
        print(f"💀 Force killed {process_type} process {pid}")
        return True
        
    except OSError as e:
        if e.errno == 3:  # No such process
            print(f"ℹ️ Process {pid} already stopped")
            return True
        else:
            print(f"❌ Error stopping process {pid}: {e}")
            return False
    except Exception as e:
        print(f"❌ Unexpected error stopping process {pid}: {e}")
        return False

def main():
    print("🛑 Pathfinder Server Shutdown")
    print("=" * 40)
    
    print("🔍 Looking for Pathfinder processes...")
    processes = find_pathfinder_processes()
    
    if not processes:
        print("ℹ️ No Pathfinder server processes found")
        print("✅ Server appears to be already stopped")
        return True
    
    print(f"🎯 Found {len(processes)} process(es) to stop:")
    for pid, process_type in processes:
        print(f"   - PID {pid} ({process_type})")
    
    print("\n🛑 Stopping processes...")
    
    success_count = 0
    for pid, process_type in processes:
        if stop_process(pid, process_type):
            success_count += 1
    
    print(f"\n📊 Results: {success_count}/{len(processes)} processes stopped")
    
    if success_count == len(processes):
        print("✅ All Pathfinder processes stopped successfully!")
        return True
    else:
        print("⚠️ Some processes could not be stopped")
        return False

if __name__ == "__main__":
    try:
        success = main()
        if success:
            print("\n🎉 Server shutdown complete!")
        else:
            print("\n⚠️ Server shutdown incomplete")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n⚠️ Shutdown interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error during shutdown: {e}")
        sys.exit(1) 