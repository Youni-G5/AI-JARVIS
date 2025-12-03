"""
Action Executor
Executes validated action plans with monitoring and error handling
"""
import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime

from core.config import settings

logger = logging.getLogger(__name__)


class ActionExecutor:
    """Executes action plans safely"""
    
    async def execute_plan(
        self, 
        plan: Dict[str, Any],
        action_client: Any
    ) -> List[Dict[str, Any]]:
        """
        Execute all actions in plan sequentially or in parallel
        
        Args:
            plan: Validated execution plan
            action_client: Client for action executor service
            
        Returns:
            List of execution results
        """
        actions = plan.get("actions", [])
        results = []
        
        logger.info(f"Executing plan with {len(actions)} actions")
        
        for idx, action in enumerate(actions):
            logger.info(f"Executing action {idx+1}/{len(actions)}: {action.get('tool')}")
            
            result = await self._execute_single_action(action, action_client)
            results.append(result)
            
            # Stop on critical failure if configured
            if result.get("status") == "error" and result.get("critical"):
                logger.error("Critical action failed, stopping execution")
                break
        
        return results
    
    async def _execute_single_action(
        self,
        action: Dict[str, Any],
        action_client: Any
    ) -> Dict[str, Any]:
        """Execute single action with timeout and error handling"""
        
        start_time = datetime.now()
        action_tool = action.get("tool")
        
        try:
            # Execute with timeout
            result = await asyncio.wait_for(
                action_client.execute(action),
                timeout=settings.ACTION_TIMEOUT
            )
            
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return {
                "action": action_tool,
                "status": "success",
                "result": result,
                "execution_time": execution_time,
                "timestamp": datetime.now().isoformat(),
            }
            
        except asyncio.TimeoutError:
            logger.error(f"Action {action_tool} timed out after {settings.ACTION_TIMEOUT}s")
            return {
                "action": action_tool,
                "status": "error",
                "error": "Timeout",
                "execution_time": settings.ACTION_TIMEOUT,
                "timestamp": datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"Action {action_tool} failed: {e}", exc_info=True)
            return {
                "action": action_tool,
                "status": "error",
                "error": str(e),
                "execution_time": (datetime.now() - start_time).total_seconds(),
                "timestamp": datetime.now().isoformat(),
            }