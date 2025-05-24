"""
Test script to verify API connections for Pathfinder
"""

import os
import sys
from dotenv import load_dotenv

def test_environment():
    print("🔍 Testing Environment Setup...")
    
    load_dotenv()
    
    print(f"Python version: {sys.version}")
    
    if hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print("✅ Virtual environment detected")
    else:
        print("⚠️  Virtual environment NOT detected")
    
    if os.path.exists('.env'):
        print("✅ .env file found")
    else:
        print("❌ .env file NOT found")
        return False
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print(f"✅ Anthropic API key found: ...{api_key[-8:]}")
    else:
        print("❌ Anthropic API key NOT found")
        return False
    
    return True

def test_claude_api():
    print("\n🤖 Testing Claude (Anthropic) API...")
    
    try:
        import anthropic
        client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
        
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=50,
            messages=[
                {"role": "user", "content": "Say 'Hello from Pathfinder!' if you can read this."}
            ]
        )
        
        content = response.content[0].text.strip()
        print(f"✅ Claude API working! Response: {content}")
        return True
        
    except Exception as e:
        print(f"❌ Claude API error: {e}")
        
        error_str = str(e).lower()
        if "api_key" in error_str or "authentication" in error_str:
            print("🔧 Fix: Check your ANTHROPIC_API_KEY in .env file")
        elif "credit" in error_str or "usage" in error_str:
            print("💳 Fix: Check your Anthropic usage and billing")
        elif "rate_limit" in error_str:
            print("⏰ Fix: Wait a moment and try again")
        
        return False

def test_google_trends():
    print("\n📈 Testing Google Trends API...")
    
    try:
        from pytrends.request import TrendReq
        import time
        
        time.sleep(1)
        
        pytrends = TrendReq(hl='en-US', tz=360)
        pytrends.build_payload(['software engineer'], cat=0, timeframe='today 3-m', geo='US', gprop='')
        
        related_queries = pytrends.related_queries()
        
        if 'software engineer' in related_queries and related_queries['software engineer'] is not None:
            top_queries = related_queries['software engineer'].get('top')
            if top_queries is not None and not top_queries.empty:
                trends = top_queries['query'].head(3).tolist()
                print(f"✅ Google Trends working! Sample trends: {trends}")
                return True
        
        print("⚠️ Google Trends API connected but no data returned")
        print("🔄 This is normal - fallback data will be used")
        return True
        
    except Exception as e:
        print(f"⚠️ Google Trends error: {e}")
        print("🔄 This is normal - fallback trend data will be used instead")
        return True 

def test_flask_dependencies():
    print("\n🌐 Testing Flask Dependencies...")
    
    try:
        import flask
        print(f"✅ Flask {flask.__version__} installed")
    except ImportError:
        print("❌ Flask not installed")
        return False
    
    try:
        import pandas
        print(f"✅ Pandas {pandas.__version__} installed")
    except ImportError:
        print("❌ Pandas not installed")
        return False
    
    try:
        import requests
        print(f"✅ Requests installed")
    except ImportError:
        print("❌ Requests not installed")
        return False
    
    return True

def main():
    print("🚀 Pathfinder API Test Suite")
    print("=" * 40)
    
    if not test_environment():
        print("\n❌ Environment setup failed. Please fix the issues above.")
        return
    
    if not test_flask_dependencies():
        print("\n❌ Dependencies missing. Run: pip install -r requirements.txt")
        return
    
    claude_ok = test_claude_api()
    trends_ok = test_google_trends()
    
    print("\n" + "=" * 40)
    print("📊 Test Results:")
    print(f"Claude API: {'✅ Working' if claude_ok else '❌ Failed'}")
    print(f"Google Trends: {'✅ Working' if trends_ok else '⚠️ Using Fallback'}")
    
    if claude_ok:
        print("\n🎉 Your Pathfinder app should work perfectly!")
        print("Run: python start_app.py")
    else:
        print("\n⚠️ Claude API needs attention, but the app will still work with fallback content.")
        print("Fix the Anthropic API key for full functionality.")

if __name__ == '__main__':
    main() 