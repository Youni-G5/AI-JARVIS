"""
Action Executor Configuration
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Action executor settings"""
    
    ENABLE_SANDBOX: bool = True
    DRY_RUN_MODE: bool = False
    ACTION_TIMEOUT: int = 30
    AUDIT_LOG_ENABLED: bool = True
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()