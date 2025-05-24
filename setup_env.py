import os

def create_env_file():
    """Create .env file with required environment variables"""
    
    print("🚀 Pathfinder Environment Setup")
    print("=" * 40)
    
    if os.path.exists('.env'):
        print("⚠️  .env file already exists!")
        overwrite = input("Do you want to overwrite it? (y/N): ").lower()
        if overwrite != 'y':
            print("❌ Setup cancelled.")
            return
    
    print("\n📝 Please provide the following information:")
    
    print("\n1. Anthropic API Key:")
    print("   - Go to: https://console.anthropic.com/")
    print("   - Create an account or sign in")
    print("   - Go to API Keys section")
    print("   - Create a new API key")
    
    anthropic_key = input("\nEnter your Anthropic API key: ").strip()
    
    if not anthropic_key:
        print("❌ API key is required!")
        return
    
    import secrets
    flask_secret = secrets.token_hex(32)
    
    env_content = f"""# Anthropic Claude API Configuration
ANTHROPIC_API_KEY={anthropic_key}

# Flask Configuration
FLASK_SECRET_KEY={flask_secret}

# Optional: Debug mode
FLASK_DEBUG=True
"""
    
    try:
        with open('.env', 'w') as f:
            f.write(env_content)
        
        print("\n✅ .env file created successfully!")
        print("\n🔒 Security Note:")
        print("   - Your .env file contains sensitive information")
        print("   - It should be added to .gitignore (don't commit to version control)")
        print("   - Keep your API key secure and don't share it")
        
        print("\n🚀 Next Steps:")
        print("   1. Start your application: python start_app.py")
        print("   2. Visit: http://localhost:5001")
        print("   3. Go to Job Seeker Chat and test the AI")
        
    except Exception as e:
        print(f"❌ Error creating .env file: {e}")

if __name__ == "__main__":
    create_env_file() 