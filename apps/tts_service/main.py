"""
AI-JARVIS TTS Service
Text-to-Speech using Piper
"""
import asyncio
import logging
import os
import subprocess
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional
import uuid

from fastapi import FastAPI, HTTPException, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, StreamingResponse
from pydantic import BaseModel
import aiofiles

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Piper configuration
PIPER_BINARY = "./piper/piper"
OUTPUT_DIR = "/tmp/tts_output"


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager"""
    logger.info("🗣️ Initializing TTS Service...")
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Check if Piper is available
    if not os.path.exists(PIPER_BINARY):
        logger.warning(f"Piper binary not found at {PIPER_BINARY}")
    
    logger.info("✅ TTS Service ready")
    yield
    
    logger.info("🛑 Shutting down TTS Service")


app = FastAPI(
    title="AI-JARVIS TTS Service",
    description="Text-to-Speech service using Piper",
    version="1.0.0",
    lifespan=lifespan,
)


class TTSRequest(BaseModel):
    text: str
    voice: Optional[str] = None
    speed: Optional[float] = 1.0


class VoiceInfo(BaseModel):
    name: str
    language: str
    quality: str


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI-JARVIS TTS Service",
        "version": "1.0.0",
        "model": settings.TTS_MODEL,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    piper_available = os.path.exists(PIPER_BINARY)
    return {
        "status": "healthy" if piper_available else "degraded",
        "piper_available": piper_available
    }


@app.post("/synthesize")
async def synthesize_speech(request: TTSRequest):
    """
    Synthesize speech from text
    
    Args:
        request: TTS request with text and optional voice/speed
        
    Returns:
        Audio file (WAV)
    """
    if not request.text or not request.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty")
    
    try:
        # Generate unique filename
        audio_id = str(uuid.uuid4())
        output_file = os.path.join(OUTPUT_DIR, f"{audio_id}.wav")
        
        # Prepare Piper command
        voice_model = request.voice or settings.TTS_MODEL
        speed = request.speed or settings.TTS_VOICE_SPEED
        
        # Use espeak-ng as fallback if Piper not available
        if not os.path.exists(PIPER_BINARY):
            logger.info("Using espeak-ng fallback")
            cmd = [
                "espeak-ng",
                "-v", "fr",  # French voice
                "-s", str(int(175 * speed)),  # Speed
                "-w", output_file,
                request.text
            ]
        else:
            # Use Piper
            cmd = [
                PIPER_BINARY,
                "--model", f"/models/{voice_model}.onnx",
                "--output_file", output_file
            ]
        
        # Run synthesis
        if os.path.exists(PIPER_BINARY):
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            stdout, stderr = await process.communicate(input=request.text.encode())
            
            if process.returncode != 0:
                logger.error(f"Piper error: {stderr.decode()}")
                raise HTTPException(status_code=500, detail="Synthesis failed")
        else:
            # Use espeak-ng synchronously
            result = subprocess.run(cmd, capture_output=True)
            if result.returncode != 0:
                logger.error(f"espeak-ng error: {result.stderr.decode()}")
                raise HTTPException(status_code=500, detail="Synthesis failed")
        
        # Return audio file
        if not os.path.exists(output_file):
            raise HTTPException(status_code=500, detail="Audio generation failed")
        
        return FileResponse(
            output_file,
            media_type="audio/wav",
            filename=f"speech_{audio_id}.wav",
            background=lambda: os.remove(output_file)  # Cleanup after sending
        )
    
    except Exception as e:
        logger.error(f"Synthesis error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.websocket("/stream")
async def stream_synthesis(websocket: WebSocket):
    """
    Real-time text-to-speech streaming
    
    Client sends text, receives audio chunks
    """
    await websocket.accept()
    logger.info("WebSocket TTS client connected")
    
    try:
        while True:
            # Receive text
            data = await websocket.receive_json()
            text = data.get("text", "")
            
            if not text:
                continue
            
            # Generate audio
            audio_id = str(uuid.uuid4())
            output_file = os.path.join(OUTPUT_DIR, f"{audio_id}.wav")
            
            # Quick synthesis with espeak-ng for streaming
            cmd = [
                "espeak-ng",
                "-v", "fr",
                "-w", output_file,
                text
            ]
            
            result = subprocess.run(cmd, capture_output=True)
            
            if result.returncode == 0 and os.path.exists(output_file):
                # Read and send audio data
                async with aiofiles.open(output_file, 'rb') as f:
                    audio_data = await f.read()
                
                await websocket.send_bytes(audio_data)
                
                # Cleanup
                os.remove(output_file)
            else:
                await websocket.send_json({
                    "error": "Synthesis failed"
                })
    
    except WebSocketDisconnect:
        logger.info("WebSocket TTS client disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        await websocket.close()


@app.get("/voices", response_model=list[VoiceInfo])
async def list_voices():
    """
    List available TTS voices
    """
    # Default voices (expand based on downloaded models)
    voices = [
        VoiceInfo(name="fr_FR-siwis-medium", language="French", quality="medium"),
        VoiceInfo(name="fr_FR-tom-medium", language="French", quality="medium"),
        VoiceInfo(name="en_US-lessac-medium", language="English", quality="medium"),
    ]
    return voices


@app.get("/test")
async def test_synthesis():
    """
    Test endpoint to verify TTS is working
    """
    test_request = TTSRequest(
        text="Bonjour, je suis JARVIS, votre assistant personnel.",
        speed=1.0
    )
    return await synthesize_speech(test_request)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8002, reload=False)