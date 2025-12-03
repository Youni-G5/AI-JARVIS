"""
LLM Agent Configuration
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """LLM agent settings"""
    
    LLM_MODEL: str = "llama3.2:latest"
    LLM_ENDPOINT: str = "http://ollama:11434"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2048
    LLM_CONTEXT_WINDOW: int = 4096
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()