"""Pytest configuration and fixtures"""
import pytest
import sys
from pathlib import Path

# Add apps directory to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "apps" / "orchestrator_core"))


@pytest.fixture
def sample_action():
    """Sample action for testing"""
    return {
        "type": "system_action",
        "tool": "open_app",
        "arguments": {"name": "firefox"},
        "safety_level": "low",
        "description": "Open Firefox browser"
    }


@pytest.fixture
def sample_plan():
    """Sample execution plan for testing"""
    return {
        "intent": "Test action",
        "actions": [
            {
                "type": "system_action",
                "tool": "open_app",
                "arguments": {"name": "test"},
                "safety_level": "low"
            }
        ],
        "requires_confirmation": False,
        "estimated_duration": 2
    }