"""
Health check endpoints
"""
from fastapi import APIRouter, status
from pydantic import BaseModel
from datetime import datetime

router = APIRouter()


class HealthResponse(BaseModel):
    status: str
    timestamp: str
    version: str


@router.get("", response_model=HealthResponse, status_code=status.HTTP_200_OK)
async def health_check():
    """Basic health check endpoint"""
    return HealthResponse(
        status="healthy",
        timestamp=datetime.now().isoformat(),
        version="1.0.0"
    )


@router.get("/ready", status_code=status.HTTP_200_OK)
async def readiness_check():
    """Readiness probe for Kubernetes"""
    # TODO: Check database connections, service availability
    return {"ready": True}


@router.get("/live", status_code=status.HTTP_200_OK)
async def liveness_check():
    """Liveness probe for Kubernetes"""
    return {"alive": True}