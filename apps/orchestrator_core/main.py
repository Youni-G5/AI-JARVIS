"""
AI-JARVIS Orchestrator Core
Main entry point for the orchestration engine
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from prometheus_client import make_asgi_app

from core.orchestrator import JarvisOrchestrator
from core.config import settings
from core.logger import setup_logging
from api import health, actions, memory
from api.websocket import ConnectionManager

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager"""
    logger.info("🚀 Starting AI-JARVIS Orchestrator Core")
    
    # Initialize orchestrator
    orchestrator = JarvisOrchestrator()
    await orchestrator.initialize()
    app.state.orchestrator = orchestrator
    
    # Initialize WebSocket manager
    app.state.ws_manager = ConnectionManager()
    
    logger.info("✅ Orchestrator Core ready")
    
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down Orchestrator Core")
    await orchestrator.shutdown()


# Create FastAPI app
app = FastAPI(
    title="AI-JARVIS Orchestrator",
    description="Production-grade autonomous AI assistant orchestrator",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

# Include routers
app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(actions.router, prefix="/api/actions", tags=["actions"])
app.include_router(memory.router, prefix="/api/memory", tags=["memory"])


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI-JARVIS Orchestrator Core",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """Main WebSocket endpoint"""
    manager: ConnectionManager = app.state.ws_manager
    orchestrator: JarvisOrchestrator = app.state.orchestrator
    
    await manager.connect(websocket)
    logger.info(f"WebSocket connected. Total: {len(manager.active_connections)}")
    
    try:
        while True:
            data = await websocket.receive_json()
            response = await orchestrator.process_request(data)
            await manager.send_personal_message(response, websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)
        logger.info(f"WebSocket disconnected. Total: {len(manager.active_connections)}")
    except Exception as e:
        logger.error(f"WebSocket error: {e}", exc_info=True)
        manager.disconnect(websocket)


@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "type": type(exc).__name__}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG,
        log_level="info",
    )