#!/usr/bin/env python3
"""
Quick fix script for HackRx 6.0 dependency issues.
This script resolves the huggingface_hub and sentence-transformers conflicts.
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
    """Main fix function."""
    print("🔧 Quick Fix for HackRx 6.0 Dependencies")
    print("=" * 50)
    
    # Uninstall problematic packages
    print("\n🗑️  Removing problematic packages...")
    commands = [
        f"{sys.executable} -m pip uninstall -y sentence-transformers",
        f"{sys.executable} -m pip uninstall -y huggingface-hub",
        f"{sys.executable} -m pip uninstall -y transformers",
    ]
    
    for command in commands:
        run_command(command)
    
    # Install correct versions
    print("\n📦 Installing correct package versions...")
    install_commands = [
        f"{sys.executable} -m pip install huggingface-hub==0.19.4",
        f"{sys.executable} -m pip install transformers==4.35.2",
        f"{sys.executable} -m pip install sentence-transformers==2.2.2",
    ]
    
    success_count = 0
    for command in install_commands:
        if run_command(command):
            success_count += 1
    
    if success_count == len(install_commands):
        print("\n🎉 Dependencies fixed successfully!")
        print("You can now run: python start.py")
        print("The API will be available at: http://127.0.0.1:8000")
    else:
        print("\n⚠️  Some packages failed to install.")
        print("The system will use fallback mode with simple embeddings.")

if __name__ == "__main__":
    main() 