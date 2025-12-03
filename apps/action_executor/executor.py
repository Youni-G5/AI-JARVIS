"""
Action Executor Implementation
Handles safe execution of system and IoT actions
"""
import asyncio
import logging
import subprocess
import platform
from typing import Dict, Any, Optional
import paho.mqtt.client as mqtt

from config import settings

logger = logging.getLogger(__name__)


class ActionExecutor:
    """
    Executes actions safely with sandbox support
    """
    
    def __init__(self):
        self.mqtt_client: Optional[mqtt.Client] = None
        self.os_type = platform.system().lower()
    
    async def initialize(self):
        """Initialize executor resources"""
        logger.info("Initializing Action Executor...")
        
        # Initialize MQTT if enabled
        if settings.MQTT_ENABLED:
            try:
                self.mqtt_client = mqtt.Client()
                self.mqtt_client.username_pw_set(
                    settings.MQTT_USERNAME,
                    settings.MQTT_PASSWORD
                )
                self.mqtt_client.connect(
                    settings.MQTT_BROKER,
                    settings.MQTT_PORT,
                    60
                )
                self.mqtt_client.loop_start()
                logger.info("✅ MQTT client connected")
            except Exception as e:
                logger.warning(f"MQTT connection failed: {e}")
                self.mqtt_client = None
        
        logger.info("✅ Executor initialized")
    
    async def shutdown(self):
        """Cleanup resources"""
        if self.mqtt_client:
            self.mqtt_client.loop_stop()
            self.mqtt_client.disconnect()
    
    async def execute(self, action: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute an action
        
        Args:
            action: Action specification
            
        Returns:
            Execution result
        """
        action_type = action.get("type")
        tool = action.get("tool")
        arguments = action.get("arguments", {})
        
        # Dry-run mode
        if settings.DRY_RUN_MODE:
            logger.info(f"[DRY RUN] Would execute: {tool} with {arguments}")
            return {
                "status": "success",
                "result": "Dry run - no action taken",
                "dry_run": True
            }
        
        # Route to appropriate handler
        if action_type == "system_action":
            return await self._execute_system_action(tool, arguments)
        elif action_type == "iot_action":
            return await self._execute_iot_action(tool, arguments)
        elif action_type == "query_action":
            return await self._execute_query_action(tool, arguments)
        else:
            return {
                "status": "error",
                "error": f"Unknown action type: {action_type}"
            }
    
    async def validate(self, action: Dict[str, Any]) -> bool:
        """
        Validate action can be executed
        
        Args:
            action: Action to validate
            
        Returns:
            True if valid
        """
        tool = action.get("tool")
        action_type = action.get("type")
        
        # Check if action type is known
        valid_types = ["system_action", "iot_action", "query_action"]
        if action_type not in valid_types:
            return False
        
        # Check if tool is implemented
        if action_type == "system_action":
            valid_tools = ["open_app", "close_app", "screenshot", "send_notification", "search_web"]
            return tool in valid_tools
        
        return True
    
    async def _execute_system_action(
        self, tool: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute system action
        """
        try:
            if tool == "open_app":
                return await self._open_application(arguments.get("name"))
            
            elif tool == "screenshot":
                return await self._take_screenshot(arguments.get("path", "/tmp/screenshot.png"))
            
            elif tool == "send_notification":
                return await self._send_notification(
                    arguments.get("title", "JARVIS"),
                    arguments.get("message", "")
                )
            
            elif tool == "search_web":
                return await self._search_web(arguments.get("query"))
            
            else:
                return {
                    "status": "error",
                    "error": f"Unknown system action: {tool}"
                }
        
        except Exception as e:
            logger.error(f"System action error: {e}", exc_info=True)
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _execute_iot_action(
        self, tool: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute IoT action via MQTT
        """
        if not self.mqtt_client:
            return {
                "status": "error",
                "error": "MQTT not available"
            }
        
        try:
            topic = f"jarvis/{tool}"
            payload = str(arguments)
            
            self.mqtt_client.publish(topic, payload)
            
            return {
                "status": "success",
                "result": f"MQTT message sent to {topic}"
            }
        
        except Exception as e:
            logger.error(f"IoT action error: {e}")
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _execute_query_action(
        self, tool: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Execute query action (information retrieval)
        """
        # Placeholder for query actions
        return {
            "status": "success",
            "result": f"Query executed: {tool}"
        }
    
    async def _open_application(self, app_name: str) -> Dict[str, Any]:
        """
        Open an application
        """
        try:
            if self.os_type == "linux":
                cmd = ["xdg-open", app_name]
            elif self.os_type == "darwin":  # macOS
                cmd = ["open", "-a", app_name]
            elif self.os_type == "windows":
                cmd = ["start", app_name]
            else:
                return {"status": "error", "error": "Unsupported OS"}
            
            if settings.ENABLE_SANDBOX:
                logger.info(f"[SANDBOX] Would open: {app_name}")
                return {
                    "status": "success",
                    "result": f"Sandboxed - would open {app_name}"
                }
            
            process = await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            
            return {
                "status": "success",
                "result": f"Opened {app_name}"
            }
        
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _take_screenshot(self, path: str) -> Dict[str, Any]:
        """
        Take a screenshot
        """
        try:
            import pyautogui
            
            screenshot = pyautogui.screenshot()
            screenshot.save(path)
            
            return {
                "status": "success",
                "result": f"Screenshot saved to {path}",
                "path": path
            }
        
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _send_notification(
        self, title: str, message: str
    ) -> Dict[str, Any]:
        """
        Send system notification
        """
        try:
            if self.os_type == "linux":
                cmd = ["notify-send", title, message]
            elif self.os_type == "darwin":
                cmd = ["osascript", "-e", f'display notification "{message}" with title "{title}"']
            elif self.os_type == "windows":
                # Windows notification requires PowerShell
                return {
                    "status": "success",
                    "result": "Notification sent (Windows simulated)"
                }
            else:
                return {"status": "error", "error": "Unsupported OS"}
            
            await asyncio.create_subprocess_exec(
                *cmd,
                stdout=asyncio.subprocess.DEVNULL,
                stderr=asyncio.subprocess.DEVNULL
            )
            
            return {
                "status": "success",
                "result": "Notification sent"
            }
        
        except Exception as e:
            return {"status": "error", "error": str(e)}
    
    async def _search_web(self, query: str) -> Dict[str, Any]:
        """
        Open web search
        """
        try:
            import webbrowser
            
            search_url = f"https://www.google.com/search?q={query}"
            
            if settings.ENABLE_SANDBOX:
                return {
                    "status": "success",
                    "result": f"Sandboxed - would search: {query}"
                }
            
            webbrowser.open(search_url)
            
            return {
                "status": "success",
                "result": f"Opened search for: {query}"
            }
        
        except Exception as e:
            return {"status": "error", "error": str(e)}