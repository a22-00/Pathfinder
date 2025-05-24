# 🚀 Deployment Checklist

## ✅ Pre-Deploy

### Environment
- [ ] Python 3.8+
- [ ] Virtual environment active
- [ ] Dependencies installed
- [ ] `.env` with ANTHROPIC_API_KEY
- [ ] FLASK_SECRET_KEY set

### Testing
- [ ] `python test_complete_system.py` passes
- [ ] `python quick_start.py` works
- [ ] Chat functionality works
- [ ] Assessment system works
- [ ] Mobile responsive

### Security
- [ ] API keys not in code
- [ ] `.env` in `.gitignore`
- [ ] Strong secret keys

## 🚀 Deploy Options

### Local
```bash
python quick_start.py
```

### Production
```bash
gunicorn wsgi:application --bind 0.0.0.0:5001
```

### Heroku
```bash
echo "web: gunicorn wsgi:application" > Procfile
heroku create your-app
heroku config:set ANTHROPIC_API_KEY=your_key
git push heroku main
```

## 🧪 Post-Deploy Tests
1. Homepage loads
2. Chat works  
3. Assessment generates
4. Mobile works

## 🆘 Troubleshooting

| Issue | Fix |
|-------|-----|
| API Key Error | Check .env |
| Import Errors | pip install -r requirements.txt |
| Port in Use | Change port |
| Template Error | Check templates/ dir |

## 📊 Success = ✅ All Tests Pass

---
**Ready? Run: `python test_complete_system.py`** 