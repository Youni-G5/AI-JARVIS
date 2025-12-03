"""
STT Service Configuration
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """STT service settings"""
    
    STT_MODEL: str = "base"
    STT_LANGUAGE: str = "fr"  # or "auto" for auto-detection
    STT_DEVICE: str = "cpu"  # or "cuda" for GPU
    WHISPER_MODEL_PATH: str = "/models"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()