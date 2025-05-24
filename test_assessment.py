import requests
import json

BASE_URL = "http://127.0.0.1:5001"

def test_assessment_system():
    print("🧪 Testing Assessment System...")
    
    print("\n1. Testing assessment creation...")
    start_data = {"topic": "Python Programming"}
    
    try:
        response = requests.post(f"{BASE_URL}/start-assessment", 
                               json=start_data, 
                               timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Assessment created successfully")
            print(f"   Session ID: {result.get('session_id')}")
            print(f"   Topic: {result.get('topic')}")
            print(f"   Total Questions: {result.get('total_questions')}")
            
            if result.get('first_question'):
                print("\n2. Testing answer submission...")
                session_id = result.get('session_id')
                
                answer_data = {
                    "session_id": session_id,
                    "answer": "A"
                }
                
                answer_response = requests.post(f"{BASE_URL}/submit-answer", 
                                              json=answer_data, 
                                              timeout=30)
                
                if answer_response.status_code == 200:
                    answer_result = answer_response.json()
                    print(f"✅ Answer submitted successfully")
                    print(f"   Correct: {answer_result.get('is_correct')}")
                    print(f"   Progress: {answer_result.get('progress', {})}")
                else:
                    print(f"❌ Answer submission failed: {answer_response.status_code}")
                    print(f"   Response: {answer_response.text}")
            
        else:
            print(f"❌ Assessment creation failed: {response.status_code}")
            print(f"   Response: {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("❌ Connection failed - make sure the server is running on port 5001")
    except requests.exceptions.Timeout:
        print("❌ Request timed out - server might be overloaded")
    except Exception as e:
        print(f"❌ Test failed: {e}")

def test_api_routes():
    print("\n🔗 Testing API route accessibility...")
    
    routes_to_test = [
        ("/", "GET"),
        ("/assessment", "GET"),
        ("/api/trends", "GET")
    ]
    
    for route, method in routes_to_test:
        try:
            if method == "GET":
                response = requests.get(f"{BASE_URL}{route}", timeout=10)
            else:
                response = requests.post(f"{BASE_URL}{route}", timeout=10)
                
            if response.status_code in [200, 404]:
                print(f"✅ {method} {route} - Status: {response.status_code}")
            else:
                print(f"⚠️ {method} {route} - Status: {response.status_code}")
                
        except Exception as e:
            print(f"❌ {method} {route} - Error: {e}")

if __name__ == "__main__":
    print("🚀 Starting Assessment System Tests")
    print("=" * 50)
    
    test_api_routes()
    test_assessment_system()
    
    print("\n" + "=" * 50)
    print("✨ Test completed! Check results above.") 