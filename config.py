from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # Environment
    ENVIRONMENT: str = "production"  # development, production, live
    
    # Security
    SECRET_KEY: str 
    ADMIN_USERNAME: str 
    ADMIN_PASSWORD_HASH: str 
    
    # Email
    SMTP_SERVER: str
    SMTP_PORT: int
    SMTP_USERNAME: str
    SMTP_PASSWORD: str
    
    # Database Configuration
    # For development: always SQLite
    # For production/live: MySQL or PostgreSQL based on DB_TYPE
    DB_TYPE: Optional[str] = "mysql"  # mysql, postgresql (only for production/live)
    DB_HOST: Optional[str] = "localhost"
    DB_PORT: Optional[int] = 3306
    DB_USER: Optional[str] = "tgmi"
    DB_PASSWORD: Optional[str] = "tgmiadmin"
    DB_NAME: Optional[str] = "tgmi"
    
    # SQLite database path (for development)
    SQLITE_DB_PATH: str = "./glorious_church.db"
    
    class Config:
        env_file = ".env"
        case_sensitive = False

settings = Settings()

