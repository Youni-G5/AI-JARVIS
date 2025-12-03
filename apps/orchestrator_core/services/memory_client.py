"""
Memory Service Client
Communicates with vector memory (ChromaDB) for context retrieval
"""
import aiohttp
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)


class MemoryClient:
    """
    Client for memory service communication
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
        self.collection_name = "jarvis_memory"
    
    async def connect(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        logger.info(f"Memory client connected to {self.base_url}")
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            logger.info("Memory client connection closed")
    
    async def search(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Search vector memory for relevant context
        
        Args:
            query: Search query
            limit: Maximum number of results
            
        Returns:
            List of relevant memory entries
        """
        if not self.session:
            raise RuntimeError("Memory client not connected")
        
        try:
            async with self.session.post(
                f"{self.base_url}/api/v1/collections/{self.collection_name}/query",
                json={
                    "query_texts": [query],
                    "n_results": limit
                },
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                data = await response.json()
                
                # Parse ChromaDB response
                results = []
                if "documents" in data and data["documents"]:
                    for doc, metadata in zip(
                        data["documents"][0], 
                        data.get("metadatas", [[]])[0]
                    ):
                        results.append({
                            "content": doc,
                            "metadata": metadata
                        })
                
                return results
        
        except aiohttp.ClientError as e:
            logger.error(f"Memory search failed: {e}")
            return []
    
    async def store(self, entry: Dict[str, Any]) -> bool:
        """
        Store entry in vector memory
        
        Args:
            entry: Memory entry to store
            
        Returns:
            Success status
        """
        if not self.session:
            raise RuntimeError("Memory client not connected")
        
        try:
            # Generate unique ID
            entry_id = entry.get("request_id", str(hash(str(entry))))
            
            async with self.session.post(
                f"{self.base_url}/api/v1/collections/{self.collection_name}/add",
                json={
                    "ids": [entry_id],
                    "documents": [entry.get("content", "")],
                    "metadatas": [entry]
                },
                timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                response.raise_for_status()
                return True
        
        except aiohttp.ClientError as e:
            logger.error(f"Memory storage failed: {e}")
            return False