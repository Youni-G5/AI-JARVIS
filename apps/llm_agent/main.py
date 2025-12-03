"""
AI-JARVIS LLM Agent
Local LLM reasoning service using Ollama
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Optional, Dict, Any, List

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
import aiohttp

from config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class GenerateRequest(BaseModel):
    prompt: str = Field(..., description="Input prompt for LLM")
    temperature: Optional[float] = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: Optional[int] = Field(default=2048, ge=1, le=8192)
    system: Optional[str] = Field(default=None, description="System prompt")
    stream: Optional[bool] = Field(default=False)


class GenerateResponse(BaseModel):
    text: str
    model: str
    tokens: int
    completion_time: float


class ChatMessage(BaseModel):
    role: str = Field(..., pattern="^(system|user|assistant)$")
    content: str


class ChatRequest(BaseModel):
    messages: List[ChatMessage]
    temperature: Optional[float] = 0.7
    max_tokens: Optional[int] = 2048


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager"""
    logger.info("🧠 Starting LLM Agent Service")
    
    # Check Ollama connection
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(f"{settings.LLM_ENDPOINT}/api/tags") as response:
                if response.status == 200:
                    data = await response.json()
                    models = data.get("models", [])
                    logger.info(f"Connected to Ollama. Available models: {len(models)}")
                else:
                    logger.warning("Ollama not ready yet, will retry on requests")
    except Exception as e:
        logger.warning(f"Could not connect to Ollama: {e}")
    
    logger.info("✅ LLM Agent Service ready")
    yield
    
    logger.info("🛑 Shutting down LLM Agent Service")


app = FastAPI(
    title="AI-JARVIS LLM Agent",
    description="Local LLM reasoning service",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI-JARVIS LLM Agent",
        "version": "1.0.0",
        "model": settings.LLM_MODEL,
        "endpoint": settings.LLM_ENDPOINT,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    # Check Ollama connection
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{settings.LLM_ENDPOINT}/api/tags",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                ollama_healthy = response.status == 200
    except Exception:
        ollama_healthy = False
    
    return {
        "status": "healthy" if ollama_healthy else "degraded",
        "ollama_connected": ollama_healthy
    }


@app.post("/generate", response_model=GenerateResponse)
async def generate_text(request: GenerateRequest):
    """
    Generate text completion from LLM
    
    Args:
        request: Generation request with prompt and parameters
        
    Returns:
        Generated text with metadata
    """
    try:
        import time
        start_time = time.time()
        
        # Prepare Ollama request
        ollama_request = {
            "model": settings.LLM_MODEL,
            "prompt": request.prompt,
            "stream": request.stream,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            }
        }
        
        if request.system:
            ollama_request["system"] = request.system
        
        # Call Ollama API
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.LLM_ENDPOINT}/api/generate",
                json=ollama_request,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                response.raise_for_status()
                
                if request.stream:
                    # Handle streaming response
                    full_text = ""
                    async for line in response.content:
                        if line:
                            import json
                            chunk = json.loads(line)
                            full_text += chunk.get("response", "")
                            if chunk.get("done", False):
                                break
                else:
                    # Non-streaming response
                    data = await response.json()
                    full_text = data.get("response", "")
        
        completion_time = time.time() - start_time
        
        return GenerateResponse(
            text=full_text,
            model=settings.LLM_MODEL,
            tokens=len(full_text.split()),  # Approximate token count
            completion_time=completion_time
        )
    
    except aiohttp.ClientError as e:
        logger.error(f"Ollama API error: {e}")
        raise HTTPException(status_code=503, detail="LLM service unavailable")
    except Exception as e:
        logger.error(f"Generation error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat_completion(request: ChatRequest):
    """
    Chat completion with conversation history
    
    Args:
        request: Chat request with message history
        
    Returns:
        Assistant response
    """
    try:
        # Convert messages to Ollama chat format
        messages = [
            {"role": msg.role, "content": msg.content}
            for msg in request.messages
        ]
        
        ollama_request = {
            "model": settings.LLM_MODEL,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": request.temperature,
                "num_predict": request.max_tokens,
            }
        }
        
        # Call Ollama chat API
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.LLM_ENDPOINT}/api/chat",
                json=ollama_request,
                timeout=aiohttp.ClientTimeout(total=120)
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                return {
                    "message": data.get("message", {}),
                    "model": settings.LLM_MODEL,
                    "done": data.get("done", False)
                }
    
    except Exception as e:
        logger.error(f"Chat error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/models")
async def list_models():
    """
    List available LLM models
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"{settings.LLM_ENDPOINT}/api/tags",
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                return {
                    "models": data.get("models", []),
                    "current_model": settings.LLM_MODEL
                }
    except Exception as e:
        logger.error(f"Failed to list models: {e}")
        return {
            "models": [],
            "current_model": settings.LLM_MODEL,
            "error": str(e)
        }


@app.post("/pull")
async def pull_model(model: str):
    """
    Pull a new model from Ollama library
    """
    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"{settings.LLM_ENDPOINT}/api/pull",
                json={"name": model},
                timeout=aiohttp.ClientTimeout(total=3600)  # 1 hour for large models
            ) as response:
                response.raise_for_status()
                return {"status": "success", "model": model}
    except Exception as e:
        logger.error(f"Failed to pull model: {e}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8003, reload=False)