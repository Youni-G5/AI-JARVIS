"""
AI-JARVIS LLM Agent Service
Wrapper for Ollama LLM inference
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Dict, Any
import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import aiohttp

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global HTTP session
http_session: Optional[aiohttp.ClientSession] = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager"""
    global http_session
    
    logger.info("🧠 Initializing LLM Agent Service...")
    
    # Create HTTP session for Ollama
    http_session = aiohttp.ClientSession()
    
    # Wait for Ollama to be ready
    await wait_for_ollama()
    
    logger.info("✅ LLM Agent Service ready")
    yield
    
    # Cleanup
    if http_session:
        await http_session.close()
    
    logger.info("🛑 Shutting down LLM Agent Service")


async def wait_for_ollama(max_retries: int = 30, delay: int = 2):
    """Wait for Ollama service to be ready"""
    for i in range(max_retries):
        try:
            async with http_session.get(
                f"{settings.LLM_ENDPOINT}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                if response.status == 200:
                    logger.info("✅ Ollama is ready")
                    return
        except Exception as e:
            logger.info(f"Waiting for Ollama... ({i+1}/{max_retries})")
            await asyncio.sleep(delay)
    
    logger.warning("Ollama not available, service will work in degraded mode")


app = FastAPI(
    title="AI-JARVIS LLM Agent Service",
    description="LLM reasoning service using Ollama",
    version="1.0.0",
    lifespan=lifespan,
)


class GenerateRequest(BaseModel):
    prompt: str
    model: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: Optional[bool] = False
    system: Optional[str] = None


class ChatMessage(BaseModel):
    role: str  # system, user, assistant
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]
    model: Optional[str] = None
    temperature: Optional[float] = None
    stream: Optional[bool] = False


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI-JARVIS LLM Agent Service",
        "version": "1.0.0",
        "model": settings.LLM_MODEL,
        "endpoint": settings.LLM_ENDPOINT,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        async with http_session.get(
            f"{settings.LLM_ENDPOINT}/api/tags",
            timeout=aiohttp.ClientTimeout(total=5)
        ) as response:
            ollama_healthy = response.status == 200
    except Exception:
        ollama_healthy = False
    
    return {
        "status": "healthy" if ollama_healthy else "degraded",
        "ollama_available": ollama_healthy
    }


@app.post("/generate")
async def generate_text(request: GenerateRequest):
    """
    Generate text completion from prompt
    
    Args:
        request: Generation request
        
    Returns:
        Generated text and metadata
    """
    if not http_session:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        model = request.model or settings.LLM_MODEL
        temperature = request.temperature or settings.LLM_TEMPERATURE
        max_tokens = request.max_tokens or settings.LLM_MAX_TOKENS
        
        # Build prompt with system message if provided
        full_prompt = request.prompt
        if request.system:
            full_prompt = f"{request.system}\n\n{request.prompt}"
        
        payload = {
            "model": model,
            "prompt": full_prompt,
            "stream": False,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens,
            }
        }
        
        async with http_session.post(
            f"{settings.LLM_ENDPOINT}/api/generate",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as response:
            response.raise_for_status()
            result = await response.json()
            
            return {
                "text": result.get("response", ""),
                "model": model,
                "done": result.get("done", True),
                "context": result.get("context", []),
                "total_duration": result.get("total_duration"),
                "eval_count": result.get("eval_count"),
            }
    
    except aiohttp.ClientError as e:
        logger.error(f"Ollama request failed: {e}")
        raise HTTPException(status_code=502, detail="LLM service unavailable")
    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat_completion(request: ChatRequest):
    """
    Chat completion with message history
    
    Args:
        request: Chat request with messages
        
    Returns:
        Assistant response
    """
    if not http_session:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        model = request.model or settings.LLM_MODEL
        temperature = request.temperature or settings.LLM_TEMPERATURE
        
        # Convert messages to Ollama format
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        payload = {
            "model": model,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }
        
        async with http_session.post(
            f"{settings.LLM_ENDPOINT}/api/chat",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=120)
        ) as response:
            response.raise_for_status()
            result = await response.json()
            
            return {
                "message": result.get("message", {}),
                "model": model,
                "done": result.get("done", True),
                "total_duration": result.get("total_duration"),
            }
    
    except aiohttp.ClientError as e:
        logger.error(f"Ollama chat failed: {e}")
        raise HTTPException(status_code=502, detail="LLM service unavailable")
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def list_models():
    """
    List available models in Ollama
    """
    if not http_session:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        async with http_session.get(
            f"{settings.LLM_ENDPOINT}/api/tags",
            timeout=aiohttp.ClientTimeout(total=10)
        ) as response:
            response.raise_for_status()
            data = await response.json()
            
            models = data.get("models", [])
            return {
                "models": [
                    {
                        "name": m.get("name"),
                        "size": m.get("size"),
                        "modified": m.get("modified_at")
                    }
                    for m in models
                ],
                "current_model": settings.LLM_MODEL
            }
    
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return {
            "models": [],
            "error": str(e)
        }


@app.post("/embed")
async def create_embeddings(text: str):
    """
    Generate embeddings for text
    
    Args:
        text: Input text
        
    Returns:
        Vector embeddings
    """
    if not http_session:
        raise HTTPException(status_code=503, detail="Service not initialized")
    
    try:
        payload = {
            "model": settings.LLM_MODEL,
            "prompt": text
        }
        
        async with http_session.post(
            f"{settings.LLM_ENDPOINT}/api/embeddings",
            json=payload,
            timeout=aiohttp.ClientTimeout(total=30)
        ) as response:
            response.raise_for_status()
            result = await response.json()
            
            return {
                "embeddings": result.get("embedding", []),
                "model": settings.LLM_MODEL
            }
    
    except Exception as e:
        logger.error(f"Embedding generation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=False)