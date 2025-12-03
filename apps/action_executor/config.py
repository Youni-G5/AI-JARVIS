"""
Action Executor Configuration
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Action executor settings"""
    
    ENABLE_SANDBOX: bool = True
    DRY_RUN_MODE: bool = False
    ACTION_TIMEOUT: int = 30
    MQTT_ENABLED: bool = False
    MQTT_BROKER: str = "mosquitto"
    MQTT_PORT: int = 1883
    MQTT_USERNAME: str = "jarvis"
    MQTT_PASSWORD: str = "changeme"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()