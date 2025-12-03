"""Configuration management using Pydantic"""
from typing import List
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Configuration
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    DEBUG: bool = False
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # LLM Configuration
    LLM_MODEL: str = "llama3.2:latest"
    LLM_ENDPOINT: str = "http://ollama:11434"
    LLM_TEMPERATURE: float = 0.7
    LLM_MAX_TOKENS: int = 2048
    
    # Security
    ENABLE_SANDBOX: bool = True
    DRY_RUN_MODE: bool = False
    MAX_CONCURRENT_ACTIONS: int = 5
    ACTION_TIMEOUT: int = 30
    AUDIT_LOG_ENABLED: bool = True
    ALLOWED_ACTIONS: List[str] = ["open_app", "search_web", "send_notification"]
    
    # Services
    STT_SERVICE_URL: str = "http://stt_service:8001"
    TTS_SERVICE_URL: str = "http://tts_service:8002"
    LLM_SERVICE_URL: str = "http://llm_agent:8003"
    VISION_SERVICE_URL: str = "http://vision_service:8004"
    MEMORY_SERVICE_URL: str = "http://chromadb:8000"
    ACTION_EXECUTOR_URL: str = "http://action_executor:8006"
    
    # Database
    DATABASE_URL: str = "postgresql://jarvis:changeme@postgres:5432/jarvis_db"
    REDIS_URL: str = "redis://:changeme@redis:6379/0"
    
    # MQTT
    MQTT_ENABLED: bool = False
    MQTT_BROKER: str = "mosquitto"
    MQTT_PORT: int = 1883
    
    # Monitoring
    ENABLE_METRICS: bool = True
    LOG_LEVEL: str = "INFO"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()