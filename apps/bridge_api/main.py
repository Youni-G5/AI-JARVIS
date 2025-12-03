"""
AI-JARVIS Bridge API
Unified gateway for all JARVIS services
"""
import logging
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import aiohttp

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="AI-JARVIS Bridge API",
    description="Unified API gateway",
    version="1.0.0",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Service endpoints
SERVICES = {
    "orchestrator": "http://orchestrator:8000",
    "stt": "http://stt_service:8001",
    "tts": "http://tts_service:8002",
    "llm": "http://llm_agent:8003",
    "vision": "http://vision_service:8004",
    "executor": "http://action_executor:8006",
}

@app.get("/")
async def root():
    return {
        "service": "AI-JARVIS Bridge API",
        "version": "1.0.0",
        "services": list(SERVICES.keys())
    }

@app.get("/health")
async def health():
    """Aggregate health check"""
    health_status = {}
    
    async with aiohttp.ClientSession() as session:
        for name, url in SERVICES.items():
            try:
                async with session.get(
                    f"{url}/health",
                    timeout=aiohttp.ClientTimeout(total=2)
                ) as response:
                    health_status[name] = response.status == 200
            except Exception:
                health_status[name] = False
    
    all_healthy = all(health_status.values())
    
    return {
        "status": "healthy" if all_healthy else "degraded",
        "services": health_status
    }

# Proxy endpoints
@app.api_route("/api/{service}/{path:path}", methods=["GET", "POST", "PUT", "DELETE"])
async def proxy(service: str, path: str, request: Request):
    """Proxy requests to appropriate service"""
    
    if service not in SERVICES:
        raise HTTPException(status_code=404, detail=f"Service '{service}' not found")
    
    target_url = f"{SERVICES[service]}/{path}"
    
    try:
        async with aiohttp.ClientSession() as session:
            # Forward request
            async with session.request(
                method=request.method,
                url=target_url,
                headers=dict(request.headers),
                data=await request.body(),
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                content = await response.read()
                return content
    
    except Exception as e:
        logger.error(f"Proxy error: {e}")
        raise HTTPException(status_code=502, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8007)