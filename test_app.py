import os
import sys

project_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_dir)

try:
    print("🔍 Testing Flask app import...")
    from project_learn_track.job_seeker import app
    print("✅ Flask app imported successfully!")
    
    print("🔍 Testing app configuration...")
    with app.app_context():
        print(f"✅ App name: {app.name}")
        print(f"✅ Database URI: {app.config.get('SQLALCHEMY_DATABASE_URI', 'Not set')}")
        print(f"✅ Secret key configured: {'Yes' if app.secret_key else 'No'}")
    
    print("🔍 Testing route registration...")
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append(f"{rule.rule} -> {rule.endpoint}")
    
    print(f"✅ Found {len(routes)} routes:")
    for route in sorted(routes):
        print(f"   {route}")
    
    print("\n✅ All tests passed! App should be ready to run.")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1) 