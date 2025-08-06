
"""
Railway-specific startup script for the HackRx API.
This script ensures proper environment configuration and startup.
"""

import os
import sys
import logging
from pathlib import Path

# Configure logging for Railway
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def setup_railway_environment():
    """Setup Railway-specific environment variables."""
    logger.info("Setting up Railway environment...")
    
    # Set default values for Railway
    os.environ.setdefault("API_HOST", "0.0.0.0")
    # Use Railway's PORT environment variable
    port = os.getenv("PORT", "8000")
    os.environ.setdefault("API_PORT", port)
    
    # Set default LLM model
    os.environ.setdefault("LLM_MODEL", "gemini-2.5-flash")
    
    # Log environment setup
    logger.info(f"API_HOST: {os.getenv('API_HOST')}")
    logger.info(f"API_PORT: {os.getenv('API_PORT')}")
    logger.info(f"PORT (Railway): {os.getenv('PORT')}")
    logger.info(f"LLM_MODEL: {os.getenv('LLM_MODEL')}")
    
    # Check required environment variables
    required_vars = ["GOOGLE_API_KEY"]
    missing_vars = [var for var in required_vars if not os.getenv(var)]
    
    if missing_vars:
        logger.warning(f"Missing environment variables: {missing_vars}")
        logger.warning("The app may not function correctly without these variables.")
    else:
        logger.info("All required environment variables are set.")

def start_application():
    """Start the FastAPI application."""
    try:
        logger.info("Starting HackRx 6.0 - Simplified PDF Processing...")
        
        # Import and start the app
        import uvicorn
        
        host = os.getenv("API_HOST", "0.0.0.0")
        port = int(os.getenv("API_PORT", "8000"))
        
        uvicorn.run(
            "app.main:app",
            host=host,
            port=port,
            log_level="info",
            reload=False,
            access_log=True
        )
        
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        import traceback
        logger.error(f"Traceback: {traceback.format_exc()}")
        sys.exit(1)

if __name__ == "__main__":
    logger.info("🚀 Railway Startup Script")
    logger.info("=" * 40)
    
    # Setup environment
    setup_railway_environment()
    
    # Start application
    start_application() 