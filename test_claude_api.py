import os
from dotenv import load_dotenv

load_dotenv()

print("🔍 CLAUDE API CONFIGURATION TEST")
print("=" * 50)

api_key = os.getenv("ANTHROPIC_API_KEY")

if not api_key:
    print("❌ ANTHROPIC_API_KEY not found in environment")
    print("📋 To fix this:")
    print("1. Create/edit your .env file")
    print("2. Add: ANTHROPIC_API_KEY=your_actual_api_key_here")
    print("3. Get API key from: https://console.anthropic.com/")
    exit(1)

print(f"✅ API Key found: {api_key[:15]}...")
print(f"📏 Length: {len(api_key)} characters")

if not api_key.startswith('sk-ant-'):
    print("⚠️ API key format looks incorrect")
    print("🔑 Anthropic API keys should start with 'sk-ant-'")
else:
    print("✅ API key format looks correct")

try:
    print("\n🔌 Testing import and client...")
    import anthropic
    
    client = anthropic.Anthropic(api_key=api_key)
    print("✅ Client initialized successfully")
    
    # Test API call
    print("🧪 Testing API call...")
    response = client.messages.create(
        model="claude-3-haiku-20240307",
        max_tokens=50,
        messages=[{"role": "user", "content": "Say 'API test successful' if you can read this."}]
    )
    
    if response and response.content:
        print("✅ API call successful!")
        print(f"📝 Response: {response.content[0].text}")
    else:
        print("❌ API call returned empty response")
        
except ImportError as e:
    print(f"❌ Import error: {e}")
    print("📦 Install anthropic: pip install anthropic")
except anthropic.AuthenticationError as e:
    print(f"❌ Authentication error: {e}")
    print("🔑 Check your API key in .env file")
except Exception as e:
    print(f"❌ Error: {e}")

print("\n" + "=" * 50)
print("✅ Test complete!") 