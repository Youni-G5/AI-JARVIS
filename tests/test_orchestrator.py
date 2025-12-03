"""
Orchestrator Core Tests
"""
import pytest
import asyncio
from apps.orchestrator_core.core.orchestrator import JarvisOrchestrator
from apps.orchestrator_core.core.planning import PlanningEngine
from apps.orchestrator_core.core.safety import SafetyValidator


@pytest.fixture
def planning_engine():
    return PlanningEngine()


@pytest.fixture
def safety_validator():
    return SafetyValidator()


def test_planning_engine_parse_valid_plan(planning_engine):
    """Test parsing valid JSON plan"""
    llm_output = '''
    {
        "intent": "Open Firefox browser",
        "actions": [
            {
                "type": "system_action",
                "tool": "open_app",
                "arguments": {"name": "firefox"},
                "safety_level": "low",
                "description": "Launch Firefox"
            }
        ],
        "requires_confirmation": false,
        "estimated_duration": 2
    }
    '''
    
    plan = planning_engine.parse_plan(llm_output)
    
    assert plan["intent"] == "Open Firefox browser"
    assert len(plan["actions"]) == 1
    assert plan["actions"][0]["tool"] == "open_app"


def test_planning_engine_parse_invalid_json(planning_engine):
    """Test handling invalid JSON"""
    llm_output = "This is not JSON"
    
    plan = planning_engine.parse_plan(llm_output)
    
    assert plan["intent"] == "error"
    assert "error" in plan


@pytest.mark.asyncio
async def test_safety_validator_allowed_action(safety_validator):
    """Test validation of allowed action"""
    plan = {
        "actions": [
            {
                "type": "system_action",
                "tool": "open_app",
                "arguments": {"name": "firefox"},
                "safety_level": "low"
            }
        ]
    }
    
    result = await safety_validator.validate(plan)
    
    assert result["safe"] == True


@pytest.mark.asyncio
async def test_safety_validator_dangerous_command(safety_validator):
    """Test blocking dangerous command"""
    plan = {
        "actions": [
            {
                "type": "system_action",
                "tool": "execute_command",
                "arguments": {"command": "rm -rf /"},
                "safety_level": "critical"
            }
        ]
    }
    
    result = await safety_validator.validate(plan)
    
    assert result["safe"] == False
    assert "Dangerous" in result["reason"]


@pytest.mark.asyncio
async def test_safety_validator_too_many_actions(safety_validator):
    """Test limiting concurrent actions"""
    actions = [
        {
            "type": "system_action",
            "tool": "open_app",
            "arguments": {"name": f"app{i}"},
            "safety_level": "low"
        }
        for i in range(10)  # More than MAX_CONCURRENT_ACTIONS
    ]
    
    plan = {"actions": actions}
    
    result = await safety_validator.validate(plan)
    
    assert result["safe"] == False
    assert "Too many" in result["reason"]