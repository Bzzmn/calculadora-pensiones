from pydantic_settings import BaseSettings
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseSettings):
    MONGODB_URL: str = os.getenv("MONGODB_URL")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME")
    MONGODB_COLLECTION: str = os.getenv("MONGODB_COLLECTION")
    
    # Configuración SMTP
    SMTP_SERVER: str = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = os.getenv("SMTP_PORT")
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL")

    class Config:
        env_file = ".env"
        case_sensitive = True

settings = Settings() 