"""
AI-JARVIS Action Executor Service
Secure execution of system actions
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
executor: ActionExecutor = None


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator:
    """Application lifespan manager"""
    global executor
    
    logger.info("⚡ Initializing Action Executor Service...")
    
    # Initialize executor
    executor = ActionExecutor()
    await executor.initialize()
    
    logger.info("✅ Action Executor Service ready")
    yield
    
    logger.info("🛑 Shutting down Action Executor Service")
    await executor.shutdown()


app = FastAPI(
    title="AI-JARVIS Action Executor Service",
    description="Secure action execution service",
    version="1.0.0",
    lifespan=lifespan,
)


class ActionRequest(BaseModel):
    type: str
    tool: str
    arguments: Dict[str, Any]
    safety_level: str = "medium"
    description: str = ""


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "service": "AI-JARVIS Action Executor Service",
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
        "executor_ready": executor is not None
    }


@app.post("/execute")
async def execute_action(action: ActionRequest):
    """
    Execute an action
    
    Args:
        action: Action to execute
        
    Returns:
        Execution result
    """
    if executor is None:
        raise HTTPException(status_code=503, detail="Executor not initialized")
    
    try:
        logger.info(f"Executing action: {action.tool}")
        
        result = await executor.execute(action.dict())
        
        return result
    
    except Exception as e:
        logger.error(f"Action execution failed: {e}", exc_info=True)
        return {
            "status": "error",
            "error": str(e)
        }


@app.post("/validate")
async def validate_action(action: ActionRequest):
    """
    Validate action without executing
    
    Args:
        action: Action to validate
        
    Returns:
        Validation result
    """
    if executor is None:
        raise HTTPException(status_code=503, detail="Executor not initialized")
    
    try:
        is_valid = await executor.validate(action.dict())
        
        return {
            "valid": is_valid,
            "action": action.tool
        }
    
    except Exception as e:
        logger.error(f"Action validation failed: {e}")
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
            "execute_command",
            "screenshot",
            "send_notification",
            "control_volume",
            "search_web"
        ],
        "iot_actions": [
            "toggle_light",
            "set_temperature",
            "lock_door",
            "unlock_door"
        ]
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8006, reload=False)