import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    """Bot configuration from environment variables"""
    
    # CapCut Account Credentials
    CAPCUT_EMAIL: str = os.getenv("CAPCUT_EMAIL", "thehimspiredshop@gmail.com")
    CAPCUT_PASSWORD: str = os.getenv("CAPCUT_PASSWORD", "Doomsday2022")
    
    # Gmail Credentials (for IMAP)
    GMAIL_EMAIL: str = os.getenv("GMAIL_EMAIL", "thehimspiredshop@gmail.com")
    GMAIL_APP_PASSWORD: str = os.getenv("GMAIL_APP_PASSWORD", "")  # MUST BE SET
    
    # IMAP Configuration
    IMAP_HOST: str = os.getenv("IMAP_HOST", "imap.gmail.com")
    IMAP_PORT: int = int(os.getenv("IMAP_PORT", "993"))
    
    # Bot Configuration
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

settings = Settings()