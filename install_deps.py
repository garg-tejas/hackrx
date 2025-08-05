
"""
Install dependencies for PDF upload functionality.
"""

import subprocess
import sys

def install_dependencies():
    """Install required dependencies."""
    print("🔧 Installing dependencies for PDF upload functionality...")
    
    try:
        # Install google-genai for File API support
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", 
            "google-genai>=0.1.0"
        ])
        print("✅ google-genai installed successfully")
        
        # Install other required packages
        subprocess.check_call([
            sys.executable, "-m", "pip", "install", "-r", "requirements.txt"
        ])
        print("✅ All dependencies installed successfully")
        
        print("\n🎉 Installation complete! The PDF upload functionality is ready.")
        print("📝 You can test it with: python test_pdf_upload.py")
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    install_dependencies() 