"""
Action Executor Service Client
Communicates with action executor for safe command execution
"""
import aiohttp
import logging
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ActionClient:
    """
    Client for action executor service communication
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def connect(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        logger.info(f"Action client connected to {self.base_url}")
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            logger.info("Action client connection closed")
    
    async def execute(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute action through executor service
        
        Args:
            action: Action to execute
            
        Returns:
            Execution result
        """
        if not self.session:
            raise RuntimeError("Action client not connected")
        
        try:
            async with self.session.post(
                f"{self.base_url}/execute",
                json=action,
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                response.raise_for_status()
                result = await response.json()
                return result
        
        except aiohttp.ClientError as e:
            logger.error(f"Action execution failed: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def validate(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Validate action without executing
        
        Args:
            action: Action to validate
            
        Returns:
            Validation result
        """
        if not self.session:
            raise RuntimeError("Action client not connected")
        
        try:
            async with self.session.post(
                f"{self.base_url}/validate",
                json=action,
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                response.raise_for_status()
                return await response.json()
        
        except aiohttp.ClientError as e:
            logger.error(f"Action validation failed: {e}")
            return {
                "valid": False,
                "error": str(e)
            }