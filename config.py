from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    SECRET_KEY: str 
    ADMIN_USERNAME: str 
    ADMIN_PASSWORD_HASH: str 
    SMTP_SERVER:str
    SMTP_PORT:int
    SMTP_USERNAME:str
    SMTP_PASSWORD:str
    
    class Config:
        env_file = ".env"

settings = Settings()

