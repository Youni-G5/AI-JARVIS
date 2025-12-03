"""
Main Orchestrator Engine
Coordinates all JARVIS services and manages action execution
"""
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json

from core.config import settings
from core.planning import PlanningEngine
from core.safety import SafetyValidator
from core.executor import ActionExecutor
from services.llm_client import LLMClient
from services.memory_client import MemoryClient
from services.action_client import ActionClient

logger = logging.getLogger(__name__)


class JarvisOrchestrator:
    """
    Core orchestration engine
    Analyzes requests, creates execution plans, validates safety, and executes actions
    """
    
    def __init__(self):
        self.planning_engine = PlanningEngine()
        self.safety_validator = SafetyValidator()
        self.executor = ActionExecutor()
        
        # Service clients
        self.llm_client: Optional[LLMClient] = None
        self.memory_client: Optional[MemoryClient] = None
        self.action_client: Optional[ActionClient] = None
        
        self.initialized = False
        
    async def initialize(self):
        """Initialize all service connections"""
        logger.info("Initializing orchestrator components...")
        
        # Initialize service clients
        self.llm_client = LLMClient(settings.LLM_SERVICE_URL)
        self.memory_client = MemoryClient(settings.MEMORY_SERVICE_URL)
        self.action_client = ActionClient(settings.ACTION_EXECUTOR_URL)
        
        await self.llm_client.connect()
        await self.memory_client.connect()
        await self.action_client.connect()
        
        self.initialized = True
        logger.info("✅ Orchestrator initialized successfully")
        
    async def shutdown(self):
        """Cleanup resources"""
        logger.info("Shutting down orchestrator...")
        if self.llm_client:
            await self.llm_client.close()
        if self.memory_client:
            await self.memory_client.close()
        if self.action_client:
            await self.action_client.close()
            
    async def process_request(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """
        Main processing pipeline
        
        Args:
            request: User request with type, content, context
            
        Returns:
            Orchestrated response with actions, results, and metadata
        """
        if not self.initialized:
            raise RuntimeError("Orchestrator not initialized")
            
        request_id = request.get("id", datetime.now().isoformat())
        request_type = request.get("type", "unknown")
        content = request.get("content", "")
        context = request.get("context", {})
        
        logger.info(f"Processing request {request_id}: {request_type}")
        
        try:
            # Step 1: Retrieve relevant context from memory
            memory_context = await self._retrieve_memory_context(content, context)
            
            # Step 2: Generate execution plan using LLM
            plan = await self._generate_plan(content, memory_context, context)
            
            # Step 3: Validate plan safety
            validation_result = await self._validate_plan(plan)
            
            if not validation_result["safe"]:
                return {
                    "request_id": request_id,
                    "status": "rejected",
                    "reason": validation_result["reason"],
                    "timestamp": datetime.now().isoformat(),
                }
            
            # Step 4: Execute plan actions
            execution_results = await self._execute_plan(plan)
            
            # Step 5: Store interaction in memory
            await self._store_memory(request_id, content, plan, execution_results)
            
            # Step 6: Generate response
            response = await self._generate_response(
                request_id, plan, execution_results, context
            )
            
            return response
            
        except Exception as e:
            logger.error(f"Error processing request {request_id}: {e}", exc_info=True)
            return {
                "request_id": request_id,
                "status": "error",
                "error": str(e),
                "timestamp": datetime.now().isoformat(),
            }
    
    async def _retrieve_memory_context(
        self, content: str, context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Retrieve relevant context from vector memory"""
        try:
            memories = await self.memory_client.search(content, limit=5)
            return {
                "relevant_memories": memories,
                "user_preferences": context.get("user_preferences", {}),
            }
        except Exception as e:
            logger.warning(f"Memory retrieval failed: {e}")
            return {"relevant_memories": [], "user_preferences": {}}
    
    async def _generate_plan(
        self, 
        content: str, 
        memory_context: Dict[str, Any],
        request_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate execution plan using LLM + planning engine"""
        
        # Build prompt with context
        prompt = self._build_planning_prompt(content, memory_context, request_context)
        
        # Query LLM
        llm_response = await self.llm_client.generate(prompt)
        
        # Parse LLM output into structured plan
        plan = self.planning_engine.parse_plan(llm_response)
        
        logger.info(f"Generated plan with {len(plan.get('actions', []))} actions")
        return plan
    
    def _build_planning_prompt(
        self,
        content: str,
        memory_context: Dict[str, Any],
        request_context: Dict[str, Any]
    ) -> str:
        """Build prompt for LLM planning"""
        
        # Load system prompt from file
        try:
            with open("/prompts/system_orchestrator.txt", "r") as f:
                system_prompt = f.read()
        except FileNotFoundError:
            system_prompt = "You are JARVIS, an AI assistant. Generate a JSON execution plan."
        
        # Build context section
        context_section = f"""
## User Request
{content}

## Relevant Context
{json.dumps(memory_context, indent=2)}

## Available Actions
{json.dumps(settings.ALLOWED_ACTIONS, indent=2)}

## Current State
{json.dumps(request_context, indent=2)}
"""
        
        return f"{system_prompt}\n\n{context_section}\n\n## Your Task\nGenerate a JSON execution plan."
    
    async def _validate_plan(self, plan: Dict[str, Any]) -> Dict[str, bool]:
        """Validate plan safety and permissions"""
        return await self.safety_validator.validate(plan)
    
    async def _execute_plan(self, plan: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Execute all actions in plan"""
        return await self.executor.execute_plan(plan, self.action_client)
    
    async def _store_memory(
        self,
        request_id: str,
        content: str,
        plan: Dict[str, Any],
        results: List[Dict[str, Any]]
    ):
        """Store interaction in vector memory"""
        try:
            memory_entry = {
                "request_id": request_id,
                "content": content,
                "plan": plan,
                "results": results,
                "timestamp": datetime.now().isoformat(),
            }
            await self.memory_client.store(memory_entry)
        except Exception as e:
            logger.warning(f"Failed to store memory: {e}")
    
    async def _generate_response(
        self,
        request_id: str,
        plan: Dict[str, Any],
        results: List[Dict[str, Any]],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Generate final response for user"""
        
        # Check if all actions succeeded
        all_success = all(r.get("status") == "success" for r in results)
        
        return {
            "request_id": request_id,
            "status": "success" if all_success else "partial",
            "plan": plan,
            "results": results,
            "summary": self._generate_summary(plan, results),
            "timestamp": datetime.now().isoformat(),
        }
    
    def _generate_summary(
        self, plan: Dict[str, Any], results: List[Dict[str, Any]]
    ) -> str:
        """Generate human-readable summary"""
        action_count = len(results)
        success_count = sum(1 for r in results if r.get("status") == "success")
        
        return f"Executed {success_count}/{action_count} actions successfully."