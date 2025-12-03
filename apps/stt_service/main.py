"""
AI-JARVIS STT Service
Speech-to-Text using Whisper
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import io

from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.responses import JSONResponse
from faster_whisper import WhisperModel

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global model instance
whisper_model = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager"""
    global whisper_model
    
    logger.info("🎤 Loading Whisper model...")
    
    # Load Whisper model
    whisper_model = WhisperModel(
        settings.STT_MODEL,
        device=settings.STT_DEVICE,
        compute_type="int8"  # Optimized for CPU
    )
    
    logger.info("✅ STT Service ready")
    yield
    
    logger.info("🛑 Shutting down STT Service")
    whisper_model = None


app = FastAPI(
    title="AI-JARVIS STT Service",
    description="Speech-to-Text service using Whisper",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI-JARVIS STT Service",
        "version": "1.0.0",
        "model": settings.STT_MODEL,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": whisper_model is not None
    }


@app.post("/transcribe")
async def transcribe_audio(audio: UploadFile = File(...)):
    """
    Transcribe audio file to text
    
    Args:
        audio: Audio file (wav, mp3, etc.)
        
    Returns:
        Transcription with segments and metadata
    """
    if whisper_model is None:
        raise HTTPException(status_code=503, detail="Model not loaded")
    
    try:
        # Read audio file
        audio_data = await audio.read()
        
        # Save to temporary file
        temp_path = f"/tmp/audio_{id(audio_data)}.wav"
        with open(temp_path, "wb") as f:
            f.write(audio_data)
        
        # Transcribe
        segments, info = whisper_model.transcribe(
            temp_path,
            language=settings.STT_LANGUAGE if settings.STT_LANGUAGE != "auto" else None,
            vad_filter=True,  # Voice activity detection
            word_timestamps=True
        )
        
        # Format response
        result_segments = []
        full_text = ""
        
        for segment in segments:
            result_segments.append({
                "start": segment.start,
                "end": segment.end,
                "text": segment.text.strip(),
                "confidence": segment.avg_logprob
            })
            full_text += segment.text.strip() + " "
        
        # Clean up temp file
        import os
        os.remove(temp_path)
        
        return {
            "text": full_text.strip(),
            "segments": result_segments,
            "language": info.language,
            "duration": info.duration,
            "language_probability": info.language_probability
        }
    
    except Exception as e:
        logger.error(f"Transcription error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/stream")
async def stream_transcription(websocket: WebSocket):
    """
    Real-time audio streaming transcription
    
    Client sends audio chunks, receives transcription updates
    """
    await websocket.accept()
    logger.info("WebSocket STT client connected")
    
    audio_buffer = io.BytesIO()
    
    try:
        while True:
            # Receive audio chunk
            data = await websocket.receive_bytes()
            audio_buffer.write(data)
            
            # Process every 2 seconds of audio (configurable)
            if audio_buffer.tell() > 32000 * 2:  # ~2 seconds at 16kHz
                audio_buffer.seek(0)
                
                # Save chunk
                temp_path = f"/tmp/stream_{id(audio_buffer)}.wav"
                with open(temp_path, "wb") as f:
                    f.write(audio_buffer.read())
                
                # Transcribe
                segments, _ = whisper_model.transcribe(
                    temp_path,
                    language=settings.STT_LANGUAGE if settings.STT_LANGUAGE != "auto" else None
                )
                
                text = " ".join([s.text.strip() for s in segments])
                
                # Send result
                await websocket.send_json({
                    "type": "transcription",
                    "text": text,
                    "timestamp": asyncio.get_event_loop().time()
                })
                
                # Reset buffer
                audio_buffer = io.BytesIO()
                
                # Clean up
                import os
                os.remove(temp_path)
    
    except WebSocketDisconnect:
        logger.info("WebSocket STT client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        await websocket.close()


@app.get("/models")
async def list_models():
    """List available Whisper models"""
    return {
        "available_models": [
            "tiny", "base", "small", "medium", "large", "large-v2", "large-v3"
        ],
        "current_model": settings.STT_MODEL
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8001, reload=False)