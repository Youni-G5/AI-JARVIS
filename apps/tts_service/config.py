"""
TTS Service Configuration
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """TTS service settings"""
    
    TTS_MODEL: str = "fr_FR-siwis-medium"
    TTS_VOICE_SPEED: float = 1.0
    PIPER_MODEL_PATH: str = "/models"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()