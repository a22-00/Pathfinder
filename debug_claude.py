"""
Debug script to test Claude API connection - this can also help to identify issues
"""

import os
import sys
from dotenv import load_dotenv

def debug_claude_connection():
    print("🔍 Claude API Debug Script")
    print("=" * 40)
    
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("   → Run: python setup_env.py")
        return False
    
    print("✅ .env file found")
    
    load_dotenv()
    
    api_key = os.getenv("ANTHROPIC_API_KEY")
    if not api_key:
        print("❌ ANTHROPIC_API_KEY not found in .env file")
        return False
    
    if api_key == "your_anthropic_api_key_here":
        print("❌ ANTHROPIC_API_KEY is still placeholder value")
        print("   → Run: python setup_env.py")
        return False
    
    print(f"✅ API key found: ...{api_key[-8:]}")
    
    try:
        import anthropic
        print("✅ anthropic package imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import anthropic: {e}")
        print("   → Run: pip install anthropic")
        return False
    
    try:
        client = anthropic.Anthropic(api_key=api_key)
        print("✅ Anthropic client created successfully")
    except Exception as e:
        print(f"❌ Failed to create Anthropic client: {e}")
        return False
    
    try:
        print("\n🧪 Testing API call...")
        response = client.messages.create(
            model="claude-3-haiku-20240307",
            max_tokens=100,
            temperature=0.7,
            system="You are a helpful AI assistant.",
            messages=[
                {"role": "user", "content": "Say hello and confirm you're working!"}
            ]
        )
        
        content = response.content[0].text.strip()
        print(f"✅ API call successful!")
        print(f"📝 Claude response: {content}")
        return True
        
    except Exception as e:
        print(f"❌ API call failed: {e}")
        
        error_str = str(e).lower()
        if "authentication" in error_str or "api_key" in error_str:
            print("🔧 This looks like an API key issue:")
            print("   - Check if your API key is correct")
            print("   - Make sure you have credits in your Anthropic account")
            print("   - Verify the key hasn't expired")
        elif "rate_limit" in error_str:
            print("🔧 Rate limit hit - wait a moment and try again")
        elif "credit" in error_str or "usage" in error_str:
            print("🔧 Account usage issue:")
            print("   - Check your Anthropic account billing")
            print("   - You may need to add credits")
        
        return False

def main():
    success = debug_claude_connection()
    
    if success:
        print("\n🎉 Everything looks good!")
        print("   Your Claude API should work in the application")
    else:
        print("\n🔧 Issues found - please fix them and try again")
        print("\n💡 Common solutions:")
        print("   1. Run: python setup_env.py")
        print("   2. Check your Anthropic account at: https://console.anthropic.com/")
        print("   3. Ensure you have API credits")
        print("   4. Verify your API key is active")

if __name__ == "__main__":
    main() 