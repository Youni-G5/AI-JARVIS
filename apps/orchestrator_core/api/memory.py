"""
Memory management endpoints
"""
from fastapi import APIRouter, Request
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()


class MemoryQuery(BaseModel):
    query: str
    limit: Optional[int] = 5


class MemoryEntry(BaseModel):
    content: str
    metadata: dict


@router.post("/search")
async def search_memory(query: MemoryQuery, request: Request):
    """
    Search through vector memory
    """
    orchestrator = request.app.state.orchestrator
    
    try:
        results = await orchestrator.memory_client.search(
            query.query, 
            limit=query.limit
        )
        return {"results": results}
    except Exception as e:
        return {"error": str(e), "results": []}


@router.post("/store")
async def store_memory(entry: MemoryEntry, request: Request):
    """
    Store entry in vector memory
    """
    orchestrator = request.app.state.orchestrator
    
    try:
        await orchestrator.memory_client.store(entry.dict())
        return {"status": "stored"}
    except Exception as e:
        return {"error": str(e), "status": "failed"}


@router.delete("/clear")
async def clear_memory(request: Request):
    """
    Clear all memory (use with caution)
    """
    # TODO: Implement memory clearing with confirmation
    return {"status": "not_implemented"}