#!/usr/bin/env python3
"""
Installation script for HackRx 6.0 dependencies.
This script ensures all dependencies are installed with compatible versions.
"""

import subprocess
import sys
import os

def run_command(command):
    """Run a command and return success status."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {command}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {command}")
        print(f"Error: {e.stderr}")
        return False

def main():
    """Main installation function."""
    print("🚀 Installing HackRx 6.0 Dependencies")
    print("=" * 50)
    
    # Upgrade pip first
    print("\n📦 Upgrading pip...")
    run_command(f"{sys.executable} -m pip install --upgrade pip")
    
    # Install core dependencies
    print("\n📦 Installing core dependencies...")
    commands = [
        f"{sys.executable} -m pip install fastapi==0.104.1",
        f"{sys.executable} -m pip install uvicorn[standard]==0.24.0",
        f"{sys.executable} -m pip install python-multipart==0.0.6",
        f"{sys.executable} -m pip install google-generativeai==0.3.2",
        f"{sys.executable} -m pip install pinecone-client==2.2.4",
        f"{sys.executable} -m pip install faiss-cpu==1.7.4",
        f"{sys.executable} -m pip install huggingface-hub==0.16.4",
        f"{sys.executable} -m pip install sentence-transformers==2.2.2",
        f"{sys.executable} -m pip install pypdf2==3.0.1",
        f"{sys.executable} -m pip install python-docx==1.1.0",
        f"{sys.executable} -m pip install psycopg2-binary==2.9.9",
        f"{sys.executable} -m pip install sqlalchemy==2.0.23",
        f"{sys.executable} -m pip install alembic==1.12.1",
        f"{sys.executable} -m pip install pydantic==2.5.0",
        f"{sys.executable} -m pip install pydantic-settings==2.1.0",
        f"{sys.executable} -m pip install python-dotenv==1.0.0",
        f"{sys.executable} -m pip install requests==2.31.0",
        f"{sys.executable} -m pip install numpy==1.24.3",
        f"{sys.executable} -m pip install pandas==2.1.3",
        f"{sys.executable} -m pip install aiofiles==23.2.1",
        f"{sys.executable} -m pip install httpx==0.25.2",
    ]
    
    success_count = 0
    for command in commands:
        if run_command(command):
            success_count += 1
    
    print(f"\n📊 Installation Summary:")
    print(f"✅ Successfully installed: {success_count}/{len(commands)} packages")
    
    if success_count == len(commands):
        print("\n🎉 All dependencies installed successfully!")
        print("You can now run: python start.py")
    else:
        print("\n⚠️  Some packages failed to install. Please check the errors above.")
        print("You may need to install them manually or check your Python environment.")

if __name__ == "__main__":
    main() 