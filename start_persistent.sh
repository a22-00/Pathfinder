echo "🚀 Starting Pathfinder Pro with Persistent Session Storage"
echo "========================================================"

cd "/Users/akshay/Downloads/Pathfinder Project" || {
    echo "❌ Failed to navigate to workspace directory"
    exit 1
}

if [ ! -d "pathfinder_env" ]; then
    echo "❌ Virtual environment not found. Please run fix_startup_issues.py first"
    exit 1
fi

echo "🔧 Activating virtual environment..."
source pathfinder_env/bin/activate || {
    echo "❌ Failed to activate virtual environment"
    exit 1
}

mkdir -p sessions
echo "📁 Sessions directory ready"

if lsof -i :5000 >/dev/null 2>&1; then
    echo "⚠️ Port 5000 is already in use. Stopping existing process..."
    pkill -f "python.*job_seeker.py" || true
    sleep 2
    
    if lsof -i :5000 >/dev/null 2>&1; then
        echo "🔨 Force killing process on port 5000..."
        lsof -ti :5000 | xargs kill -9 || true
        sleep 1
    fi
fi

export FLASK_APP=project_learn_track/job_seeker.py
export FLASK_ENV=development
export PYTHONPATH="${PWD}:${PYTHONPATH}"

echo "🌐 Starting Flask server with persistent sessions..."
echo "📍 URL: http://localhost:5000"
echo "📁 Sessions stored in: $(pwd)/sessions"
echo "💾 Sessions now persist across server restarts!"
echo ""

python project_learn_track/job_seeker.py 