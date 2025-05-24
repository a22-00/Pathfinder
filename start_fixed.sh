#!/bin/bash
cd "/Users/akshay/Downloads/Pathfinder Project"
source .venv/bin/activate

echo "🚀 Starting Pathfinder on port 5001"
echo "📝 Server will be available at: http://localhost:5001"
echo "🛑 Press Ctrl+C to stop the server"
echo "-" * 50

export FLASK_RUN_PORT=5001
python -m gunicorn -c gunicorn.conf.py wsgi:application --bind 127.0.0.1:5001
