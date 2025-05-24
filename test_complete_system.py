import requests
import json
import time
import os
from dotenv import load_dotenv

load_dotenv()
BASE_URL = "http://localhost:5001"

def test_api_endpoints():
    print("🧪 Testing API Endpoints...")
    endpoints = [
        ("GET", "/", "Home page"),
        ("GET", "/job-seeker", "Job seeker chat"),
        ("GET", "/assessment", "Assessment page"),
        ("GET", "/api/trends?topic=Software Engineer", "Trends API"),
    ]
    
    for method, endpoint, description in endpoints:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{endpoint}")
            
            if response.status_code == 200:
                print(f"✅ {description}: SUCCESS")
            else:
                print(f"❌ {description}: FAILED ({response.status_code})")
        except requests.exceptions.ConnectionError:
            print(f"⚠️ {description}: Server not running")
        except Exception as e:
            print(f"❌ {description}: ERROR - {e}")

def test_chat_functionality():
    print("\n💬 Testing Chat...")
    try:
        chat_data = {"message": "I'm interested in becoming a data scientist. What skills should I focus on?"}
        response = requests.post(f"{BASE_URL}/chat", json=chat_data)
        
        if response.status_code == 200:
            result = response.json()
            if 'response' in result and len(result['response']) > 50:
                print("✅ Chat with Claude: SUCCESS")
                print(f"📝 Response preview: {result['response'][:100]}...")
            else:
                print("⚠️ Chat response too short or missing")
        else:
            print(f"❌ Chat failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Chat test error: {e}")

def test_assessment_system():
    print("\n📝 Testing Assessment...")
    try:
        assessment_data = {"topic": "Python Programming"}
        response = requests.post(f"{BASE_URL}/start-assessment", json=assessment_data)
        
        if response.status_code == 200:
            result = response.json()
            if 'session_id' in result and 'first_question' in result:
                print("✅ Assessment start: SUCCESS")
                print(f"📋 Session: {result['session_id']}")
                return result['session_id']
            else:
                print("⚠️ Assessment start response incomplete")
        else:
            print(f"❌ Assessment start failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Assessment test error: {e}")
    return None

def test_environment_setup():
    print("\n🔧 Testing Environment...")
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if api_key:
        print(f"✅ ANTHROPIC_API_KEY: Found (...{api_key[-8:]})")
    else:
        print("❌ ANTHROPIC_API_KEY: Missing")
    
    secret_key = os.getenv("FLASK_SECRET_KEY")
    if secret_key:
        print("✅ FLASK_SECRET_KEY: Found")
    else:
        print("⚠️ FLASK_SECRET_KEY: Using default")

def run_complete_test():
    print("🚀 PATHFINDER AI - SYSTEM TEST")
    print("=" * 40)
    
    test_environment_setup()
    test_api_endpoints()
    test_chat_functionality()
    test_assessment_system()
    
    print("\n" + "=" * 40)
    print("📊 TEST COMPLETE")
    print("✅ = Ready | ❌ = Fix needed")

if __name__ == "__main__":
    run_complete_test() 