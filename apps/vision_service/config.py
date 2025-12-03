"""
Vision Service Configuration
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Vision service settings"""
    
    YOLO_MODEL: str = "yolov8n.pt"
    YOLO_CONFIDENCE: float = 0.5
    ENABLE_WEBCAM: bool = True
    ENABLE_OCR: bool = True
    TESSERACT_LANG: str = "fra+eng"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()