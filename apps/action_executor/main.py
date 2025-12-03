"""
AI-JARVIS Action Executor
Secure execution of system actions with sandboxing
"""
import asyncio
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Any

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

from config import settings
from executor import ActionExecutor

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global executor instance
action_executor: ActionExecutor = None


class ActionRequest(BaseModel):
    type: str
    tool: str
    arguments: Dict[str, Any]
    safety_level: str = "medium"
    dry_run: bool = False


class ActionResponse(BaseModel):
    status: str
    result: Any
    execution_time: float
    sandbox_used: bool


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager"""
    global action_executor
    
    logger.info("⚡ Starting Action Executor Service")
    
    # Initialize executor
    action_executor = ActionExecutor(
        sandbox_enabled=settings.ENABLE_SANDBOX,
        dry_run_mode=settings.DRY_RUN_MODE
    )
    
    logger.info("✅ Action Executor ready")
    logger.info(f"Sandbox enabled: {settings.ENABLE_SANDBOX}")
    logger.info(f"Dry-run mode: {settings.DRY_RUN_MODE}")
    
    yield
    
    logger.info("🛑 Shutting down Action Executor")
    await action_executor.cleanup()


app = FastAPI(
    title="AI-JARVIS Action Executor",
    description="Secure action execution service",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI-JARVIS Action Executor",
        "version": "1.0.0",
        "sandbox_enabled": settings.ENABLE_SANDBOX,
        "dry_run_mode": settings.DRY_RUN_MODE,
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "executor_ready": action_executor is not None
    }


@app.post("/execute", response_model=ActionResponse)
async def execute_action(request: ActionRequest):
    """
    Execute an action securely
    
    Args:
        request: Action request with type, tool, and arguments
        
    Returns:
        Execution result with status and metadata
    """
    if action_executor is None:
        raise HTTPException(status_code=503, detail="Executor not initialized")
    
    try:
        logger.info(f"Executing action: {request.tool}")
        
        result = await action_executor.execute(
            action_type=request.type,
            tool=request.tool,
            arguments=request.arguments,
            safety_level=request.safety_level,
            dry_run=request.dry_run or settings.DRY_RUN_MODE
        )
        
        return ActionResponse(**result)
    
    except Exception as e:
        logger.error(f"Execution error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/validate")
async def validate_action(request: ActionRequest):
    """
    Validate action without executing
    
    Args:
        request: Action to validate
        
    Returns:
        Validation result
    """
    if action_executor is None:
        raise HTTPException(status_code=503, detail="Executor not initialized")
    
    try:
        is_valid = await action_executor.validate(
            action_type=request.type,
            tool=request.tool,
            arguments=request.arguments
        )
        
        return {
            "valid": is_valid,
            "action": request.tool
        }
    
    except Exception as e:
        logger.error(f"Validation error: {e}", exc_info=True)
        return {
            "valid": False,
            "error": str(e)
        }


@app.get("/actions")
async def list_actions():
    """List available actions"""
    return {
        "system_actions": [
            "open_app",
            "close_app",
            "screenshot",
            "send_notification",
            "control_volume",
            "search_web"
        ],
        "iot_actions": [
            "toggle_light",
            "set_temperature"
        ],
        "description": "Available action types and tools"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8006, reload=False)