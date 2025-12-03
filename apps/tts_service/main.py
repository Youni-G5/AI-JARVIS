"""
AI-JARVIS TTS Service
Text-to-Speech using Piper
"""
import asyncio
import logging
import io
import wave
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from pydantic import BaseModel
import numpy as np
import soundfile as sf

try:
    from piper import PiperVoice
    PIPER_AVAILABLE = True
except ImportError:
    PIPER_AVAILABLE = False
    logging.warning("Piper not available, using mock mode")

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global voice instance
piper_voice: Optional[PiperVoice] = None


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    speed: Optional[float] = 1.0


class TTSResponse(BaseModel):
    audio_url: str
    duration: float
    sample_rate: int


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager"""
    global piper_voice
    
    logger.info("🗣️ Loading Piper TTS model...")
    
    if PIPER_AVAILABLE:
        try:
            # Load Piper voice model
            model_path = f"{settings.PIPER_MODEL_PATH}/{settings.TTS_MODEL}.onnx"
            config_path = f"{settings.PIPER_MODEL_PATH}/{settings.TTS_MODEL}.onnx.json"
            
            piper_voice = PiperVoice.load(model_path, config_path)
            logger.info(f"✅ TTS Service ready with model: {settings.TTS_MODEL}")
        except Exception as e:
            logger.error(f"Failed to load Piper model: {e}")
            logger.info("Running in mock mode")
    else:
        logger.info("Running in mock mode (Piper not installed)")
    
    yield
    
    logger.info("🛑 Shutting down TTS Service")
    piper_voice = None


app = FastAPI(
    title="AI-JARVIS TTS Service",
    description="Text-to-Speech service using Piper",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI-JARVIS TTS Service",
        "version": "1.0.0",
        "model": settings.TTS_MODEL,
        "status": "operational",
        "piper_available": PIPER_AVAILABLE
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "model_loaded": piper_voice is not None or not PIPER_AVAILABLE
    }


@app.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    """
    Synthesize speech from text
    
    Args:
        request: TTS request with text and options
        
    Returns:
        Audio file (WAV format)
    """
    if not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        if PIPER_AVAILABLE and piper_voice:
            # Real Piper synthesis
            audio_stream = io.BytesIO()
            wav_file = wave.open(audio_stream, "wb")
            
            # Configure WAV file
            wav_file.setnchannels(1)  # Mono
            wav_file.setsampwidth(2)  # 16-bit
            wav_file.setframerate(piper_voice.config.sample_rate)
            
            # Synthesize
            audio_data = []
            for audio_chunk in piper_voice.synthesize_stream_raw(
                request.text,
                speaker_id=None,
                length_scale=1.0 / request.speed
            ):
                audio_data.extend(audio_chunk)
            
            # Convert to bytes
            audio_array = np.array(audio_data, dtype=np.int16)
            wav_file.writeframes(audio_array.tobytes())
            wav_file.close()
            
            audio_stream.seek(0)
            
            return StreamingResponse(
                audio_stream,
                media_type="audio/wav",
                headers={
                    "Content-Disposition": "attachment; filename=speech.wav"
                }
            )
        else:
            # Mock mode - return silent audio
            logger.warning("Using mock TTS (Piper not available)")
            duration = len(request.text.split()) * 0.3  # ~0.3s per word
            sample_rate = 22050
            
            # Generate silent audio
            audio_data = np.zeros(int(duration * sample_rate), dtype=np.int16)
            
            audio_stream = io.BytesIO()
            sf.write(audio_stream, audio_data, sample_rate, format='WAV')
            audio_stream.seek(0)
            
            return StreamingResponse(
                audio_stream,
                media_type="audio/wav",
                headers={
                    "Content-Disposition": "attachment; filename=speech.wav"
                }
            )
    
    except Exception as e:
        logger.error(f"TTS synthesis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/voices")
async def list_voices():
    """
    List available voices
    """
    return {
        "available_voices": [
            "fr_FR-siwis-medium",
            "fr_FR-upmc-medium",
            "en_US-lessac-medium",
            "en_GB-alan-medium",
            "es_ES-sharvard-medium",
            "de_DE-thorsten-medium"
        ],
        "current_voice": settings.TTS_MODEL,
        "description": "Piper TTS supports multiple languages and voices"
    }


@app.post("/test")
async def test_voice(text: str = "Bonjour, je suis JARVIS, votre assistant personnel."):
    """
    Test TTS with sample text
    """
    request = TTSRequest(text=text)
    return await synthesize_speech(request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=False)