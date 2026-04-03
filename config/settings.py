# config/settings.py
# Configuration de l'agent avec Pydantic Settings

from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    # Clés API
    openai_api_key: str = ""
    anthropic_key: str = ""
    openrouter_key: str = ""
    
    # Modèle
    model_name: str = "gpt-4o"
    
    # Chemins
    db_path: str = "agent.db"
    memory_db_path: str = "agent_memory.db"
    
    # Limites
    max_iterations: int = 20
    tool_timeout: int = 30
    sandbox_dir: str = "/tmp/agent"
    
    max_retries: int = 2
    
    # Chemins additionnels
    tasks_file: str = "/tmp/agent/tasks.json"
    logs_dir: str = "logs"
    
    # Feature flags
    enable_tracing: bool = False
    langsmith_api_key: str = ""
    langsmith_project: str = "agent"
    
    # Telegram
    telegram_bot_token: str = ""
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


# Instance globale de configuration
settings = Settings()