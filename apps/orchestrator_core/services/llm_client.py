"""
LLM Service Client
Communicates with LLM agent for reasoning and plan generation
"""
import aiohttp
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)


class LLMClient:
    """
    Client for LLM service communication
    """
    
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session: Optional[aiohttp.ClientSession] = None
    
    async def connect(self):
        """Initialize HTTP session"""
        self.session = aiohttp.ClientSession()
        logger.info(f"LLM client connected to {self.base_url}")
    
    async def close(self):
        """Close HTTP session"""
        if self.session:
            await self.session.close()
            logger.info("LLM client connection closed")
    
    async def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate text from LLM
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated text
        """
        if not self.session:
            raise RuntimeError("LLM client not connected")
        
        try:
            async with self.session.post(
                f"{self.base_url}/generate",
                json={"prompt": prompt, **kwargs},
                timeout=aiohttp.ClientTimeout(total=60)
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("text", "")
        
        except aiohttp.ClientError as e:
            logger.error(f"LLM generation failed: {e}")
            raise
    
    async def health_check(self) -> bool:
        """Check if LLM service is healthy"""
        if not self.session:
            return False
        
        try:
            async with self.session.get(
                f"{self.base_url}/health",
                timeout=aiohttp.ClientTimeout(total=5)
            ) as response:
                return response.status == 200
        except Exception:
            return False