# Pathfinder AI

**Claude-powered learning companion** for students and job seekers.

## ✨ Features
- 🎓 Assessment quizzes with learning plans
- 💼 Interview prep materials
- 📈 Industry trends integration
- 🧠 Personalized recommendations

## 🚀 Quick Start

```bash
python quick_start.py
```

## Manual Setup

1. **Install**
```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

2. **Configure**
```bash
echo "ANTHROPIC_API_KEY=your_key" > .env
```

3. **Run**
```bash
python start_app.py
```

## Test
```bash
python test_complete_system.py
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| API key error | Check .env file |
| Import errors | Run pip install -r requirements.txt |
| Port in use | Change port in job_seeker.py |

---