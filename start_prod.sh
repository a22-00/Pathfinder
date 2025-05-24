echo "🚀 Starting Pathfinder Production Server"
echo "========================================"

if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "⚠️  Virtual environment not detected!"
    echo "Activating virtual environment..."
    
    if [ -d "venv" ]; then
        source venv/bin/activate
        echo "✅ Virtual environment activated"
    else
        echo "❌ Virtual environment 'venv' not found!"
        echo "Please create it first: python -m venv venv"
        exit 1
    fi
fi

if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found!"
    echo "Please create it or run: python setup_env.py"
    exit 1
fi

echo "🏭 Starting Gunicorn server..."
echo "📝 Server will be available at: http://localhost:5001"
echo "🛑 Press Ctrl+C to stop"

exec gunicorn -c gunicorn.conf.py wsgi:application 