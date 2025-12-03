"""
Action execution endpoints
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Dict, Any, List, Optional

router = APIRouter()


class ActionRequest(BaseModel):
    type: str
    content: str
    context: Optional[Dict[str, Any]] = {}


class ActionResponse(BaseModel):
    request_id: str
    status: str
    plan: Dict[str, Any]
    results: List[Dict[str, Any]]
    summary: str
    timestamp: str


@router.post("/execute", response_model=ActionResponse)
async def execute_action(action_request: ActionRequest, request: Request):
    """
    Execute an action request through the orchestrator
    """
    orchestrator = request.app.state.orchestrator
    
    request_data = {
        "type": action_request.type,
        "content": action_request.content,
        "context": action_request.context
    }
    
    response = await orchestrator.process_request(request_data)
    
    if response.get("status") == "error":
        raise HTTPException(status_code=500, detail=response.get("error"))
    
    return response


@router.get("/history")
async def get_action_history():
    """
    Get action execution history
    """
    # TODO: Implement action history retrieval from database
    return {"history": []}


@router.get("/allowed")
async def get_allowed_actions():
    """
    Get list of allowed actions
    """
    from core.config import settings
    return {"allowed_actions": settings.ALLOWED_ACTIONS}