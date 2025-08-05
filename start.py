
"""
Startup script for HackRx 6.0 system.
This script provides an easy way to start the application with proper configuration.
"""

import os
import sys
import uvicorn
from pathlib import Path

def check_environment():
    """Check if required environment variables are set."""
    required_vars = [
        'GOOGLE_API_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("⚠️  Warning: The following environment variables are not set:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nYou can set them in your .env file or environment.")
        print("The system will work with default values for testing.")
    
    return len(missing_vars) == 0

def main():
    """Main startup function."""
    print("🚀 Starting HackRx 6.0 - Simplified PDF Processing")
    print("=" * 60)
    
    # Check environment
    env_ok = check_environment()
    
    # Get configuration
    host = os.getenv('API_HOST', '0.0.0.0')
    port = int(os.getenv('API_PORT', '8000'))
    
    print(f"📍 API will be available at: http://{host}:{port}")
    print(f"📚 API Documentation: http://{host}:{port}/docs")
    print(f"🔍 Interactive API docs: http://{host}:{port}/redoc")
    
    if not env_ok:
        print("\n⚠️  Running in test mode - some features may be limited")
    
    print("\n" + "=" * 60)
    
    try:
        # Start the application
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            reload=True,
            log_level="info"
        )
    except KeyboardInterrupt:
        print("\n👋 Shutting down HackRx 6.0 - Simplified PDF Processing...")
    except Exception as e:
        print(f"\n❌ Error starting application: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main() 