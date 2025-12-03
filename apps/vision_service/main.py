"""
AI-JARVIS Vision Service
Computer vision with YOLOv8 + OCR
"""
import asyncio
import logging
import io
import base64
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, List, Dict, Any

from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import cv2
import numpy as np
from PIL import Image
import pytesseract
from ultralytics import YOLO

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instances
yolo_model: Optional[YOLO] = None


class DetectionResult(BaseModel):
    class_name: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]


class VisionResponse(BaseModel):
    detections: List[DetectionResult]
    image_size: tuple
    processing_time: float


class OCRResult(BaseModel):
    text: str
    confidence: float
    bbox: Optional[List[int]] = None


class OCRResponse(BaseModel):
    full_text: str
    blocks: List[OCRResult]
    language: str


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager"""
    global yolo_model
    
    logger.info("👁️ Loading YOLO model...")
    
    try:
        # Load YOLO model
        model_path = f"/models/{settings.YOLO_MODEL}"
        yolo_model = YOLO(model_path)
        logger.info(f"✅ Vision Service ready with {settings.YOLO_MODEL}")
    except Exception as e:
        logger.error(f"Failed to load YOLO model: {e}")
        logger.info("Vision service will use default model")
        yolo_model = YOLO("yolov8n.pt")  # Fallback to nano model
    
    yield
    
    logger.info("🛑 Shutting down Vision Service")
    yolo_model = None


app = FastAPI(
    title="AI-JARVIS Vision Service",
    description="Computer vision and OCR service",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI-JARVIS Vision Service",
        "version": "1.0.0",
        "model": settings.YOLO_MODEL,
        "ocr_enabled": settings.ENABLE_OCR,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": yolo_model is not None,
        "ocr_available": settings.ENABLE_OCR
    }


@app.post("/detect", response_model=VisionResponse)
async def detect_objects(image: UploadFile = File(...)):
    """
    Detect objects in image using YOLO
    
    Args:
        image: Image file
        
    Returns:
        Detection results with bounding boxes and confidences
    """
    if yolo_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        import time
        start_time = time.time()
        
        # Read image
        image_data = await image.read()
        nparr = np.frombuffer(image_data, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        if img is None:
            raise HTTPException(status_code=400, detail="Invalid image")
        
        # Run detection
        results = yolo_model.predict(
            img,
            conf=settings.YOLO_CONFIDENCE,
            verbose=False
        )
        
        # Parse results
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                # Get box coordinates
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                
                # Get class and confidence
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                class_name = result.names[class_id]
                
                detections.append(DetectionResult(
                    class_name=class_name,
                    confidence=confidence,
                    bbox=[x1, y1, x2, y2]
                ))
        
        processing_time = time.time() - start_time
        
        return VisionResponse(
            detections=detections,
            image_size=img.shape[:2],
            processing_time=processing_time
        )
    
    except Exception as e:
        logger.error(f"Detection error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ocr", response_model=OCRResponse)
async def extract_text(image: UploadFile = File(...)):
    """
    Extract text from image using OCR
    
    Args:
        image: Image file
        
    Returns:
        Extracted text with confidence scores
    """
    if not settings.ENABLE_OCR:
        raise HTTPException(status_code=503, detail="OCR not enabled")
    
    try:
        # Read image
        image_data = await image.read()
        img = Image.open(io.BytesIO(image_data))
        
        # Run OCR with detailed output
        ocr_data = pytesseract.image_to_data(
            img,
            lang=settings.TESSERACT_LANG,
            output_type=pytesseract.Output.DICT
        )
        
        # Extract full text
        full_text = pytesseract.image_to_string(
            img,
            lang=settings.TESSERACT_LANG
        )
        
        # Parse blocks with confidence > 0
        blocks = []
        n_boxes = len(ocr_data['text'])
        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            conf = float(ocr_data['conf'][i])
            
            if text and conf > 0:
                bbox = [
                    ocr_data['left'][i],
                    ocr_data['top'][i],
                    ocr_data['width'][i],
                    ocr_data['height'][i]
                ]
                
                blocks.append(OCRResult(
                    text=text,
                    confidence=conf / 100.0,  # Convert to 0-1 scale
                    bbox=bbox
                ))
        
        return OCRResponse(
            full_text=full_text.strip(),
            blocks=blocks,
            language=settings.TESSERACT_LANG
        )
    
    except Exception as e:
        logger.error(f"OCR error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze")
async def analyze_scene(image: UploadFile = File(...)):
    """
    Complete scene analysis: object detection + OCR
    
    Args:
        image: Image file
        
    Returns:
        Combined detection and OCR results
    """
    try:
        # Read image once
        image_data = await image.read()
        
        # Create UploadFile objects for each service
        detection_image = UploadFile(
            filename=image.filename,
            file=io.BytesIO(image_data)
        )
        ocr_image = UploadFile(
            filename=image.filename,
            file=io.BytesIO(image_data)
        )
        
        # Run detection and OCR concurrently
        detection_task = detect_objects(detection_image)
        ocr_task = extract_text(ocr_image) if settings.ENABLE_OCR else None
        
        if ocr_task:
            detection_result, ocr_result = await asyncio.gather(
                detection_task,
                ocr_task,
                return_exceptions=True
            )
        else:
            detection_result = await detection_task
            ocr_result = None
        
        return {
            "detection": detection_result if not isinstance(detection_result, Exception) else {"error": str(detection_result)},
            "ocr": ocr_result if not isinstance(ocr_result, Exception) else {"error": str(ocr_result)},
            "status": "complete"
        }
    
    except Exception as e:
        logger.error(f"Scene analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def list_models():
    """List available YOLO models"""
    return {
        "available_models": [
            "yolov8n.pt", "yolov8s.pt", "yolov8m.pt",
            "yolov8l.pt", "yolov8x.pt"
        ],
        "current_model": settings.YOLO_MODEL,
        "description": "YOLOv8 models from nano to extra-large"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=False)