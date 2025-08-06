from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.routes import router
from app.config import settings
import logging
import os
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Create FastAPI app
app = FastAPI(
    title="HackRx 6.0 - Simplified PDF Processing",
    description="Streamlined document query system using Google Gemini AI for direct PDF processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(router, prefix=settings.API_PREFIX)

@app.get("/")
async def root():
    """Root endpoint with system information."""
    return {
        "message": "HackRx 6.0 - Simplified PDF Processing",
        "version": "1.0.0",
        "status": "healthy",
        "timestamp": datetime.now(timezone.utc).isoformat().replace('+00:00', 'Z'),
        "endpoints": {
            "main": "/api/v1/hackrx/run",
            "health": "/api/v1/health",
            "docs": "/docs",
            "redoc": "/redoc"
        }
    }

@app.get("/health") 
@app.get("/api/v1/health")
async def health():
    """Health check for Railway with API prefix."""
    return {
        "status": "ok"
    }

@app.on_event("startup")
async def startup_event():
    """Application startup event."""
    logging.info("Starting HackRx 6.0 - Simplified PDF Processing...")
    host = os.getenv("API_HOST", settings.API_HOST)
    port = os.getenv("PORT", str(settings.API_PORT))
    logging.info(f"API will be available at http://{host}:{port}")
    logging.info(f"API documentation at http://{host}:{port}/docs")

@app.on_event("shutdown")
async def shutdown_event():
    """Application shutdown event."""
    logging.info("Shutting down HackRx 6.0 - Simplified PDF Processing...")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=False  # Disable reload for production
    ) 