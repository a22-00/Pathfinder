import os
import sys
import requests
import json
import time

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

BASE_URL = "http://localhost:5000"

def test_app_startup():
    """Test if the Flask app can start"""
    print("🔍 Testing app startup...")
    try:
        from project_learn_track.job_seeker import app
        print("✅ Flask app imported successfully!")
        
        with app.app_context():
            print(f"✅ App context created successfully!")
            
        return True
    except Exception as e:
        print(f"❌ App startup failed: {e}")
        return False

def test_assessment_endpoints():
    """Test assessment functionality"""
    print("\n🎯 Testing assessment endpoints...")
    
    print("Testing /start-assessment...")
    assessment_data = {"topic": "Python Programming"}
    
    try:
        response = requests.post(f"{BASE_URL}/start-assessment", 
                               json=assessment_data, 
                               timeout=5)
        
        if response.status_code in [401, 403]:  # Unauthorized (expected)
            print("✅ /start-assessment endpoint exists (requires authentication)")
        elif response.status_code == 200:
            print("✅ /start-assessment endpoint working!")
        else:
            print(f"⚠️ /start-assessment returned {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Server not running - start with: python run_fixed_app.py")
        return False
    except Exception as e:
        print(f"❌ Assessment test failed: {e}")
        return False
    
    return True

def test_trends_api():
    """Test trends API"""
    print("\n📈 Testing trends API...")
    
    try:
        response = requests.get(f"{BASE_URL}/api/trends?topic=Software Engineer", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            if 'trends' in data and isinstance(data['trends'], list):
                print(f"✅ Trends API working! Got {len(data['trends'])} trends")
                print(f"   Sample trends: {data['trends'][:3]}")
                return True
            else:
                print("❌ Trends API returned invalid data format")
        else:
            print(f"❌ Trends API returned {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Server not running - start with: python run_fixed_app.py")
        return False
    except Exception as e:
        print(f"❌ Trends API test failed: {e}")
        return False
    
    return False

def test_dashboard_route():
    """Test dashboard route"""
    print("\n🏠 Testing dashboard route...")
    
    try:
        response = requests.get(f"{BASE_URL}/dashboard", timeout=5)
        
        if response.status_code in [401, 403]:  # Unauthorized (expected)
            print("✅ /dashboard endpoint exists (requires authentication)")
            return True
        elif response.status_code == 200:
            print("✅ /dashboard endpoint accessible!")
            return True
        else:
            print(f"⚠️ /dashboard returned {response.status_code}")
            
    except requests.exceptions.ConnectionError:
        print("⚠️ Server not running - start with: python run_fixed_app.py")
        return False
    except Exception as e:
        print(f"❌ Dashboard test failed: {e}")
        return False
    
    return True

def test_template_files():
    """Test template files exist and are readable"""
    print("\n📄 Testing template files...")
    
    templates = [
        'templates/assessment.html',
        'templates/job_seeker_chat.html', 
        'templates/dashboard/index.html',
        'templates/auth/setup.html',
        'templates/auth/login.html',
        'templates/auth/register.html'
    ]
    
    success = True
    for template in templates:
        try:
            with open(template, 'r', encoding='utf-8') as f:
                content = f.read()
                if len(content) > 100:  # Basic check for non-empty
                    print(f"✅ {template} - OK")
                else:
                    print(f"⚠️ {template} - Too short")
                    success = False
        except FileNotFoundError:
            print(f"❌ {template} - Not found")
            success = False
        except Exception as e:
            print(f"❌ {template} - Error: {e}")
            success = False
    
    return success

def main():
    """Run all tests"""
    print("🧪 Running comprehensive test suite for fixes...\n")
    
    tests = [
        ("App Startup", test_app_startup),
        ("Template Files", test_template_files),
        ("Assessment Endpoints", test_assessment_endpoints),
        ("Trends API", test_trends_api),
        ("Dashboard Route", test_dashboard_route),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    print("\n" + "="*50)
    print("📊 TEST RESULTS SUMMARY")
    print("="*50)
    
    all_passed = True
    for test_name, passed in results.items():
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{test_name:20} {status}")
        if not passed:
            all_passed = False
    
    print("="*50)
    if all_passed:
        print("🎉 ALL TESTS PASSED!")
        print("\n💡 To start the application:")
        print("   python run_fixed_app.py")
        print("\n🌐 Then visit: http://localhost:5000")
    else:
        print("⚠️  SOME TESTS FAILED")
        print("\n🔧 Check the error messages above and:")
        print("   1. Make sure all dependencies are installed")
        print("   2. Start the server: python run_fixed_app.py")
        print("   3. Re-run this test")
    
    return 0 if all_passed else 1

if __name__ == "__main__":
    sys.exit(main()) 