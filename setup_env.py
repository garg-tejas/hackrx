#!/usr/bin/env python3
"""
Environment setup script for HackRx 6.0.
This script helps create and configure the .env file.
"""

import os
import shutil

def create_env_file():
    """Create .env file from example if it doesn't exist."""
    if not os.path.exists('.env'):
        if os.path.exists('env.example'):
            shutil.copy('env.example', '.env')
            print("✅ Created .env file from env.example")
        else:
            print("❌ env.example not found")
            return False
    else:
        print("✅ .env file already exists")
    
    return True

def check_env_variables():
    """Check if required environment variables are set."""
    required_vars = [
        'GOOGLE_API_KEY',
        'PINECONE_API_KEY',
        'PINECONE_ENVIRONMENT'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("\n⚠️  The following environment variables are not set:")
        for var in missing_vars:
            print(f"   - {var}")
        
        print("\n📝 To set them up:")
        print("1. Edit the .env file in this directory")
        print("2. Add your API keys:")
        print("   GOOGLE_API_KEY=your_google_api_key")
        print("   PINECONE_API_KEY=your_pinecone_api_key")
        print("   PINECONE_ENVIRONMENT=your_pinecone_environment")
        print("\n🔗 Get API keys from:")
        print("   - Google: https://makersuite.google.com/app/apikey")
        print("   - Pinecone: https://app.pinecone.io/")
        
        return False
    else:
        print("✅ All required environment variables are set")
        return True

def main():
    """Main setup function."""
    print("🚀 Setting up HackRx 6.0 Environment")
    print("=" * 40)
    
    # Create .env file
    if create_env_file():
        print("\n📋 Environment file ready")
    else:
        print("\n❌ Failed to create environment file")
        return
    
    # Check environment variables
    env_ok = check_env_variables()
    
    if env_ok:
        print("\n🎉 Environment setup complete!")
        print("You can now run: python start.py")
    else:
        print("\n⚠️  Please set up your environment variables before running the application.")

if __name__ == "__main__":
    main() 