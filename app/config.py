import os
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

load_dotenv()

class Settings(BaseSettings):
    # API Configuration
    API_HOST: str = "127.0.0.1"  # Default for local development
    API_PORT: int = 8000
    API_PREFIX: str = "/api/v1"
    
    # External APIs
    GOOGLE_API_KEY: str
    HACKRX_API_TOKEN: str = "018fbf34e584c6effc325d2b54ba468383140299330b71b644cb73775d410be5"
    
    # LLM Configuration
    LLM_MODEL: str = "gemini-2.5-flash"
    MAX_TOKENS: int = 1500
    TEMPERATURE: float = 0.1
    
    class Config:
        env_file = ".env"
        extra = "ignore"  # Ignore extra environment variables

settings = Settings() 