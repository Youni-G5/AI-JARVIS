"""
Planning Engine
Parses LLM output into structured execution plans
"""
import json
import logging
from typing import Dict, Any, List
from pydantic import BaseModel, Field, ValidationError

logger = logging.getLogger(__name__)


class Action(BaseModel):
    """Single action model"""
    type: str = Field(..., description="Action type")
    tool: str = Field(..., description="Tool/command to execute")
    arguments: Dict[str, Any] = Field(default_factory=dict)
    safety_level: str = Field(default="medium", pattern="^(low|medium|high|critical)$")
    description: str = Field(default="")


class ExecutionPlan(BaseModel):
    """Complete execution plan"""
    intent: str = Field(..., description="Understood user intent")
    actions: List[Action] = Field(default_factory=list)
    requires_confirmation: bool = Field(default=False)
    estimated_duration: int = Field(default=0, description="Estimated duration in seconds")


class PlanningEngine:
    """Parses and validates LLM-generated plans"""
    
    def parse_plan(self, llm_output: str) -> Dict[str, Any]:
        """
        Parse LLM output into structured plan
        
        Args:
            llm_output: Raw LLM response (should be JSON)
            
        Returns:
            Validated execution plan
        """
        try:
            # Try to extract JSON from markdown code blocks
            if "```json" in llm_output:
                start = llm_output.find("```json") + 7
                end = llm_output.find("```", start)
                llm_output = llm_output[start:end].strip()
            elif "```" in llm_output:
                start = llm_output.find("```") + 3
                end = llm_output.find("```", start)
                llm_output = llm_output[start:end].strip()
            
            # Parse JSON
            plan_dict = json.loads(llm_output)
            
            # Validate with Pydantic
            plan = ExecutionPlan(**plan_dict)
            
            logger.info(f"Parsed plan: {plan.intent} with {len(plan.actions)} actions")
            return plan.model_dump()
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse JSON plan: {e}")
            return self._create_error_plan("Invalid JSON format")
            
        except ValidationError as e:
            logger.error(f"Plan validation failed: {e}")
            return self._create_error_plan("Plan validation failed")
            
        except Exception as e:
            logger.error(f"Unexpected planning error: {e}", exc_info=True)
            return self._create_error_plan(str(e))
    
    def _create_error_plan(self, reason: str) -> Dict[str, Any]:
        """Create an error plan"""
        return {
            "intent": "error",
            "actions": [],
            "requires_confirmation": False,
            "estimated_duration": 0,
            "error": reason,
        }