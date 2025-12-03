"""
AI-JARVIS Vision Service
Computer vision with YOLOv8 and OCR
"""
import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, List, Dict, Any
import io
import base64

from fastapi import FastAPI, UploadFile, File, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from pydantic import BaseModel
import cv2
import numpy as np
from ultralytics import YOLO
import pytesseract
from PIL import Image

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instances
yolo_model: Optional[YOLO] = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager"""
    global yolo_model
    
    logger.info("👁️ Loading Vision models...")
    
    # Load YOLO model
    try:
        model_path = f"/models/{settings.YOLO_MODEL}"
        if not os.path.exists(model_path):
            logger.warning(f"YOLO model not found at {model_path}, downloading...")
            yolo_model = YOLO(settings.YOLO_MODEL)  # Will auto-download
        else:
            yolo_model = YOLO(model_path)
        
        logger.info(f"✅ YOLO model loaded: {settings.YOLO_MODEL}")
    except Exception as e:
        logger.error(f"Failed to load YOLO model: {e}")
        yolo_model = None
    
    logger.info("✅ Vision Service ready")
    yield
    
    logger.info("🛑 Shutting down Vision Service")


app = FastAPI(
    title="AI-JARVIS Vision Service",
    description="Computer vision service with YOLOv8 and OCR",
    version="1.0.0",
    lifespan=lifespan,
)


class DetectionResult(BaseModel):
    label: str
    confidence: float
    bbox: List[float]  # [x1, y1, x2, y2]


class OCRResult(BaseModel):
    text: str
    confidence: float
    bbox: Optional[List[int]] = None


class VisionResponse(BaseModel):
    detections: List[DetectionResult]
    ocr_results: List[OCRResult]
    image_size: List[int]  # [width, height]
    processing_time: float


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI-JARVIS Vision Service",
        "version": "1.0.0",
        "yolo_model": settings.YOLO_MODEL,
        "ocr_enabled": settings.ENABLE_OCR,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "yolo_loaded": yolo_model is not None,
        "ocr_available": settings.ENABLE_OCR
    }


@app.post("/detect")
async def detect_objects(image: UploadFile = File(...)):
    """
    Detect objects in image using YOLOv8
    
    Args:
        image: Image file (jpg, png, etc.)
        
    Returns:
        Detection results with bounding boxes and labels
    """
    if yolo_model is None:
        raise HTTPException(status_code=503, detail="YOLO model not loaded")
    
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
        results = yolo_model(img, conf=settings.YOLO_CONFIDENCE)
        
        # Parse results
        detections = []
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                label = yolo_model.names[class_id]
                
                detections.append(DetectionResult(
                    label=label,
                    confidence=confidence,
                    bbox=[x1, y1, x2, y2]
                ))
        
        processing_time = time.time() - start_time
        
        return {
            "detections": detections,
            "ocr_results": [],
            "image_size": [img.shape[1], img.shape[0]],
            "processing_time": processing_time
        }
    
    except Exception as e:
        logger.error(f"Detection error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/ocr")
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
        import time
        start_time = time.time()
        
        # Read image
        image_data = await image.read()
        img = Image.open(io.BytesIO(image_data))
        
        # Run OCR
        ocr_data = pytesseract.image_to_data(
            img,
            lang=settings.TESSERACT_LANG,
            output_type=pytesseract.Output.DICT
        )
        
        # Parse results
        ocr_results = []
        n_boxes = len(ocr_data['text'])
        
        for i in range(n_boxes):
            text = ocr_data['text'][i].strip()
            if text:
                confidence = float(ocr_data['conf'][i]) / 100.0
                x, y, w, h = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
                
                ocr_results.append(OCRResult(
                    text=text,
                    confidence=confidence,
                    bbox=[x, y, x+w, y+h]
                ))
        
        processing_time = time.time() - start_time
        
        # Combine all text
        full_text = " ".join([r.text for r in ocr_results])
        
        return {
            "full_text": full_text,
            "ocr_results": ocr_results,
            "processing_time": processing_time
        }
    
    except Exception as e:
        logger.error(f"OCR error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/analyze")
async def analyze_image(image: UploadFile = File(...)):
    """
    Complete image analysis: object detection + OCR
    
    Args:
        image: Image file
        
    Returns:
        Combined detection and OCR results
    """
    if yolo_model is None:
        raise HTTPException(status_code=503, detail="YOLO model not loaded")
    
    try:
        import time
        start_time = time.time()
        
        # Read image
        image_data = await image.read()
        nparr = np.frombuffer(image_data, np.uint8)
        img_cv = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Object detection
        results = yolo_model(img_cv, conf=settings.YOLO_CONFIDENCE)
        detections = []
        
        for result in results:
            boxes = result.boxes
            for box in boxes:
                x1, y1, x2, y2 = box.xyxy[0].tolist()
                confidence = float(box.conf[0])
                class_id = int(box.cls[0])
                label = yolo_model.names[class_id]
                
                detections.append(DetectionResult(
                    label=label,
                    confidence=confidence,
                    bbox=[x1, y1, x2, y2]
                ))
        
        # OCR
        ocr_results = []
        if settings.ENABLE_OCR:
            img_pil = Image.open(io.BytesIO(image_data))
            ocr_data = pytesseract.image_to_data(
                img_pil,
                lang=settings.TESSERACT_LANG,
                output_type=pytesseract.Output.DICT
            )
            
            n_boxes = len(ocr_data['text'])
            for i in range(n_boxes):
                text = ocr_data['text'][i].strip()
                if text:
                    confidence = float(ocr_data['conf'][i]) / 100.0
                    x, y, w, h = ocr_data['left'][i], ocr_data['top'][i], ocr_data['width'][i], ocr_data['height'][i]
                    
                    ocr_results.append(OCRResult(
                        text=text,
                        confidence=confidence,
                        bbox=[x, y, x+w, y+h]
                    ))
        
        processing_time = time.time() - start_time
        
        return VisionResponse(
            detections=detections,
            ocr_results=ocr_results,
            image_size=[img_cv.shape[1], img_cv.shape[0]],
            processing_time=processing_time
        )
    
    except Exception as e:
        logger.error(f"Analysis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/stream")
async def stream_video_analysis(websocket: WebSocket):
    """
    Real-time video stream analysis
    
    Client sends video frames, receives detection results
    """
    await websocket.accept()
    logger.info("WebSocket vision client connected")
    
    try:
        while True:
            # Receive frame
            data = await websocket.receive_bytes()
            
            # Decode frame
            nparr = np.frombuffer(data, np.uint8)
            frame = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            
            if frame is None:
                continue
            
            # Run detection
            if yolo_model:
                results = yolo_model(frame, conf=settings.YOLO_CONFIDENCE, verbose=False)
                
                detections = []
                for result in results:
                    boxes = result.boxes
                    for box in boxes:
                        x1, y1, x2, y2 = box.xyxy[0].tolist()
                        confidence = float(box.conf[0])
                        class_id = int(box.cls[0])
                        label = yolo_model.names[class_id]
                        
                        detections.append({
                            "label": label,
                            "confidence": confidence,
                            "bbox": [x1, y1, x2, y2]
                        })
                
                # Send results
                await websocket.send_json({
                    "type": "detections",
                    "detections": detections,
                    "count": len(detections)
                })
    
    except WebSocketDisconnect:
        logger.info("WebSocket vision client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        await websocket.close()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8004, reload=False)