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
    ALLOWED_HOSTS: List[str] = []

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "ignore"

    @validator("ALLOWED_HOSTS", pre=True)
    def parse_allowed_hosts(cls, v) -> List[str]:
        """Convierte JSON string de hosts a lista"""
        hosts = []
        
        # Agregar hosts por defecto para desarrollo local
        if os.getenv("ENVIRONMENT") == "development":
            hosts.extend([
                "http://localhost:3000",
                "http://localhost:8000"
            ])
        
        # Leer hosts desde variable de entorno
        allowed_hosts_str = os.getenv("ALLOWED_HOSTS", "[]")
        try:
            # Limpiar la cadena de comillas simples si existen
            allowed_hosts_str = allowed_hosts_str.replace("'", '"')
            json_hosts = json.loads(allowed_hosts_str)
            if isinstance(json_hosts, list):
                hosts.extend(json_hosts)
        except json.JSONDecodeError as e:
            print(f"Error parsing ALLOWED_HOSTS JSON: {e}")
            print(f"Raw value: {allowed_hosts_str}")
        
        # Asegurar que el frontend URL esté incluido
        frontend_url = os.getenv("THEFULLSTACK_FRONTEND_URL")
        if frontend_url:
            hosts.append(frontend_url)
        
        # Eliminar duplicados y valores vacíos
        return list(set(host for host in hosts if host))

settings = Settings() 