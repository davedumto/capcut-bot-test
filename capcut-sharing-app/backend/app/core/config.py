from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    database_url: str
    bot_service_url: str = "http://localhost:5000"
    frontend_url: str = "http://localhost:3000"
    secret_key: str
    gmail_user: str
    gmail_app_password: str
    environment: str = "development"
    
    class Config:
        env_file = ".env"


settings = Settings()