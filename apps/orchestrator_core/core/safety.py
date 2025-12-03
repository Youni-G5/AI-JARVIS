"""
Safety Validator
Multi-layer validation for action execution
"""
import logging
from typing import Dict, Any, List
import yaml

from core.config import settings

logger = logging.getLogger(__name__)


class SafetyValidator:
    """Validates action plans for safety and permissions"""
    
    def __init__(self):
        self.allowed_actions = set(settings.ALLOWED_ACTIONS)
        self.sandbox_enabled = settings.ENABLE_SANDBOX
        self.dry_run = settings.DRY_RUN_MODE
        
        # Load permission rules
        self.permission_rules = self._load_permission_rules()
    
    def _load_permission_rules(self) -> Dict[str, Any]:
        """Load permission rules from YAML"""
        try:
            with open("/prompts/permissions.yml", "r") as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            logger.warning("Permission rules file not found, using defaults")
            return self._get_default_permissions()
    
    def _get_default_permissions(self) -> Dict[str, Any]:
        """Default permission rules"""
        return {
            "system_actions": {
                "open_app": {"level": "low", "requires_confirmation": False},
                "close_app": {"level": "low", "requires_confirmation": False},
                "screenshot": {"level": "low", "requires_confirmation": False},
                "execute_command": {"level": "critical", "requires_confirmation": True},
                "file_write": {"level": "high", "requires_confirmation": True},
                "file_delete": {"level": "critical", "requires_confirmation": True},
            },
            "iot_actions": {
                "toggle_light": {"level": "low", "requires_confirmation": False},
                "set_temperature": {"level": "medium", "requires_confirmation": False},
                "unlock_door": {"level": "critical", "requires_confirmation": True},
            }
        }
    
    async def validate(self, plan: Dict[str, Any]) -> Dict[str, bool]:
        """
        Validate execution plan
        
        Returns:
            {"safe": bool, "reason": str, "requires_confirmation": bool}
        """
        actions = plan.get("actions", [])
        
        if not actions:
            return {"safe": True, "reason": "No actions to execute"}
        
        # Validate each action
        for action in actions:
            validation = self._validate_action(action)
            if not validation["safe"]:
                return validation
        
        # Check concurrency limits
        if len(actions) > settings.MAX_CONCURRENT_ACTIONS:
            return {
                "safe": False,
                "reason": f"Too many concurrent actions ({len(actions)} > {settings.MAX_CONCURRENT_ACTIONS})"
            }
        
        # Check if plan requires confirmation
        requires_confirmation = any(
            self._action_requires_confirmation(action) for action in actions
        )
        
        return {
            "safe": True,
            "reason": "Plan validated successfully",
            "requires_confirmation": requires_confirmation
        }
    
    def _validate_action(self, action: Dict[str, Any]) -> Dict[str, bool]:
        """Validate single action"""
        action_type = action.get("type")
        tool = action.get("tool")
        safety_level = action.get("safety_level", "medium")
        
        # Check if action is allowed
        if tool not in self.allowed_actions:
            return {
                "safe": False,
                "reason": f"Action '{tool}' not in allowed list"
            }
        
        # Check safety level
        if safety_level == "critical" and not self.sandbox_enabled:
            return {
                "safe": False,
                "reason": f"Critical action '{tool}' requires sandbox"
            }
        
        # Validate arguments
        validation = self._validate_arguments(action)
        if not validation["safe"]:
            return validation
        
        return {"safe": True, "reason": "Action validated"}
    
    def _validate_arguments(self, action: Dict[str, Any]) -> Dict[str, bool]:
        """Validate action arguments"""
        tool = action.get("tool")
        arguments = action.get("arguments", {})
        
        # Add specific validation rules per tool
        if tool == "execute_command":
            command = arguments.get("command", "")
            # Block dangerous commands
            dangerous_keywords = ["rm -rf", "dd if=", "mkfs", "> /dev"]
            if any(keyword in command for keyword in dangerous_keywords):
                return {
                    "safe": False,
                    "reason": f"Dangerous command detected: {command}"
                }
        
        return {"safe": True, "reason": "Arguments valid"}
    
    def _action_requires_confirmation(self, action: Dict[str, Any]) -> bool:
        """Check if action requires user confirmation"""
        action_type = action.get("type")
        tool = action.get("tool")
        safety_level = action.get("safety_level", "medium")
        
        # Critical actions always require confirmation
        if safety_level == "critical":
            return True
        
        # Check permission rules
        rules = self.permission_rules.get(action_type, {})
        tool_rule = rules.get(tool, {})
        
        return tool_rule.get("requires_confirmation", False)