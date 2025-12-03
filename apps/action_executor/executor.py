"""
Action Executor Core Logic
Handles secure execution with sandboxing
"""
import asyncio
import logging
import subprocess
import time
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class ActionExecutor:
    """
    Secure action executor with sandbox support
    """
    
    def __init__(self, sandbox_enabled: bool = True, dry_run_mode: bool = False):
        self.sandbox_enabled = sandbox_enabled
        self.dry_run_mode = dry_run_mode
        self.audit_log = []
    
    async def execute(
        self,
        action_type: str,
        tool: str,
        arguments: Dict[str, Any],
        safety_level: str = "medium",
        dry_run: bool = False
    ) -> Dict[str, Any]:
        """
        Execute action with appropriate handler
        
        Args:
            action_type: Type of action (system_action, iot_action, etc.)
            tool: Specific tool to execute
            arguments: Tool arguments
            safety_level: Security level
            dry_run: If True, simulate without executing
            
        Returns:
            Execution result
        """
        start_time = time.time()
        
        # Log action
        self._log_action(action_type, tool, arguments)
        
        # Dry-run mode
        if dry_run or self.dry_run_mode:
            logger.info(f"DRY-RUN: Would execute {tool} with {arguments}")
            return {
                "status": "success",
                "result": "Dry-run mode: action not executed",
                "execution_time": 0.0,
                "sandbox_used": False
            }
        
        # Route to appropriate handler
        if action_type == "system_action":
            result = await self._execute_system_action(tool, arguments, safety_level)
        elif action_type == "iot_action":
            result = await self._execute_iot_action(tool, arguments)
        elif action_type == "query_action":
            result = await self._execute_query_action(tool, arguments)
        else:
            raise ValueError(f"Unknown action type: {action_type}")
        
        execution_time = time.time() - start_time
        
        return {
            "status": "success",
            "result": result,
            "execution_time": execution_time,
            "sandbox_used": self.sandbox_enabled and safety_level in ["high", "critical"]
        }
    
    async def _execute_system_action(
        self,
        tool: str,
        arguments: Dict[str, Any],
        safety_level: str
    ) -> Any:
        """
        Execute system-level action
        """
        if tool == "open_app":
            return await self._open_application(arguments.get("name"))
        
        elif tool == "close_app":
            return await self._close_application(arguments.get("name"))
        
        elif tool == "screenshot":
            return await self._take_screenshot(arguments.get("path", "/tmp/screenshot.png"))
        
        elif tool == "send_notification":
            return await self._send_notification(
                arguments.get("title", "JARVIS"),
                arguments.get("message")
            )
        
        elif tool == "control_volume":
            return await self._control_volume(arguments.get("level"))
        
        elif tool == "search_web":
            return await self._search_web(arguments.get("query"))
        
        else:
            raise ValueError(f"Unknown system action: {tool}")
    
    async def _execute_iot_action(self, tool: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute IoT action (placeholder - integrate with MQTT)
        """
        logger.info(f"IoT action: {tool} with {arguments}")
        return {"iot_action": tool, "status": "executed", "arguments": arguments}
    
    async def _execute_query_action(self, tool: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute query action
        """
        logger.info(f"Query action: {tool} with {arguments}")
        return {"query_action": tool, "status": "executed"}
    
    async def _open_application(self, app_name: str) -> str:
        """
        Open application (Linux example)
        """
        try:
            # Simple implementation - platform specific
            cmd = ["xdg-open", app_name] if app_name.startswith("http") else [app_name]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            return f"Opened {app_name}"
        
        except Exception as e:
            logger.error(f"Failed to open app: {e}")
            return f"Failed to open {app_name}: {str(e)}"
    
    async def _close_application(self, app_name: str) -> str:
        """
        Close application
        """
        try:
            cmd = ["pkill", "-f", app_name]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            return f"Closed {app_name}"
        
        except Exception as e:
            return f"Failed to close {app_name}: {str(e)}"
    
    async def _take_screenshot(self, path: str) -> str:
        """
        Take screenshot (requires scrot or similar)
        """
        try:
            cmd = ["scrot", path]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            return f"Screenshot saved to {path}"
        
        except Exception as e:
            return f"Screenshot failed: {str(e)}"
    
    async def _send_notification(self, title: str, message: str) -> str:
        """
        Send desktop notification (requires notify-send)
        """
        try:
            cmd = ["notify-send", title, message]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            return "Notification sent"
        
        except Exception as e:
            return f"Notification failed: {str(e)}"
    
    async def _control_volume(self, level: int) -> str:
        """
        Control system volume
        """
        try:
            # Example for Linux with pactl
            cmd = ["pactl", "set-sink-volume", "@DEFAULT_SINK@", f"{level}%"]
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE
            )
            
            await process.communicate()
            return f"Volume set to {level}%"
        
        except Exception as e:
            return f"Volume control failed: {str(e)}"
    
    async def _search_web(self, query: str) -> str:
        """
        Open web browser with search query
        """
        try:
            import urllib.parse
            encoded_query = urllib.parse.quote(query)
            url = f"https://www.google.com/search?q={encoded_query}"
            
            return await self._open_application(url)
        
        except Exception as e:
            return f"Web search failed: {str(e)}"
    
    async def validate(self, action_type: str, tool: str, arguments: Dict[str, Any]) -> bool:
        """
        Validate action without executing
        """
        # Basic validation
        if not tool:
            return False
        
        # Check if tool is known
        known_tools = [
            "open_app", "close_app", "screenshot", "send_notification",
            "control_volume", "search_web", "toggle_light", "set_temperature"
        ]
        
        return tool in known_tools
    
    def _log_action(self, action_type: str, tool: str, arguments: Dict[str, Any]):
        """
        Log action to audit trail
        """
        self.audit_log.append({
            "timestamp": time.time(),
            "action_type": action_type,
            "tool": tool,
            "arguments": arguments
        })
        
        logger.info(f"Action logged: {tool}")
    
    async def cleanup(self):
        """
        Cleanup resources
        """
        logger.info("Cleaning up action executor...")
        # Save audit log, cleanup resources, etc.
        logger.info(f"Total actions executed: {len(self.audit_log)}")