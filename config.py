from pydantic_settings import BaseSettings
from pydantic import validator
from dotenv import load_dotenv
import os
from typing import List
import json

load_dotenv()

class Settings(BaseSettings):
    MONGODB_URL: str = os.getenv("MONGODB_URL")
    MONGODB_DB_NAME: str = os.getenv("MONGODB_DB_NAME")
    MONGODB_COLLECTION: str = os.getenv("MONGODB_COLLECTION")
    
    # Variable de entorno para el ambiente
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # Configuración SMTP
    SMTP_SERVER: str = os.getenv("SMTP_SERVER")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD")
    SENDER_EMAIL: str = os.getenv("SENDER_EMAIL")

    # Configuración de Vectorstores
    PINECONE_API_KEY: str | None = os.getenv("PINECONE_API_KEY")
    PINECONE_REGION: str | None = os.getenv("PINECONE_REGION")
    PINECONE_CLOUD: str | None = os.getenv("PINECONE_CLOUD")
    VOYAGE_API_KEY: str | None = os.getenv("VOYAGE_API_KEY")

    # Configuración de Openai con Qwen
    OPENAI_API_KEY: str | None = os.getenv("OPENAI_API_KEY")
    OPENAI_API_BASE: str | None = os.getenv("OPENAI_API_BASE")

    # Configuración de frontend
    THEFULLSTACK_FRONTEND_URL: str = os.getenv("THEFULLSTACK_FRONTEND_URL", "http://localhost:3000")
    SECRET_KEY: str = os.getenv("SECRET_KEY")

    # Agregar ALLOWED_HOSTS como lista
    ALLOWED_HOSTS: List[str] = [
        "http://localhost:3000",
        "http://localhost:8000"
    ]

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"  # Ignora variables de entorno adicionales

    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v: str | List[str]) -> List[str]:
        """Convierte JSON string de hosts a lista"""
        hosts = [
            "http://localhost:3000",
            "http://localhost:8000",
            os.getenv("THEFULLSTACK_FRONTEND_URL", "http://localhost:3000")
        ]
        
        additional_hosts = os.getenv("ALLOWED_HOSTS")
        if additional_hosts:
            try:
                json_hosts = json.loads(additional_hosts)
                if isinstance(json_hosts, list):
                    hosts.extend(json_hosts)
            except json.JSONDecodeError:
                pass
        
        return list(set(hosts))  # Eliminar duplicados

settings = Settings() 