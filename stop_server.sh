#!/bin/bash
# Simple server shutdown script for Pathfinder

echo "🛑 Stopping Pathfinder Server..."

# Method 1: Kill processes by port
echo "📍 Stopping processes on common ports..."
for port in 5001 5002 5003 5004 5005; do
    pids=$(lsof -ti:$port 2>/dev/null)
    if [ ! -z "$pids" ]; then
        echo "🔍 Found process(es) on port $port: $pids"
        echo "$pids" | xargs kill -TERM 2>/dev/null
        sleep 2
        # Force kill if still running
        remaining=$(lsof -ti:$port 2>/dev/null)
        if [ ! -z "$remaining" ]; then
            echo "💀 Force killing remaining processes on port $port"
            echo "$remaining" | xargs kill -9 2>/dev/null
        fi
    fi
done

# Method 2: Kill gunicorn processes
echo "🐍 Stopping gunicorn processes..."
pkill -f "gunicorn.*wsgi" 2>/dev/null

# Method 3: Kill python processes running our app
echo "🐍 Stopping Python app processes..."
pkill -f "python.*start_production" 2>/dev/null

echo "✅ Server shutdown complete!"
echo "ℹ️  You can now start the server again with: ./start_fixed.sh" 