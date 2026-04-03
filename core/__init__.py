# core/__init__.py
# Module core : le cerveau de l'agent V2

from core.state import AgentState
from core.schemas import ToolCallProposal, ToolResult, PlanStep, SessionSummary
from core.graph import build_graph
from core.nodes import (
    plan_node, 
    choose_action_node, 
    execute_tool_node,
    record_result_node,
    decide_node,
    PLAN_NODE,
    CHOOSE_ACTION_NODE,
    EXECUTE_TOOL_NODE,
    RECORD_RESULT_NODE,
    DECIDE_NODE,
)
from core.prompts import PLAN_PROMPT, ACT_PROMPT, DECIDE_PROMPT

__all__ = [
    "AgentState",
    "ToolCallProposal",
    "ToolResult",
    "PlanStep",
    "SessionSummary",
    "build_graph",
    "plan_node",
    "choose_action_node",
    "execute_tool_node",
    "record_result_node",
    "decide_node",
    "PLAN_NODE",
    "CHOOSE_ACTION_NODE",
    "EXECUTE_TOOL_NODE",
    "RECORD_RESULT_NODE",
    "DECIDE_NODE",
    "PLAN_PROMPT",
    "ACT_PROMPT",
    "DECIDE_PROMPT",
]

def __getattr__(name):
    if name == "inject_memory_context":
        from memory.session import inject_memory_context
        return inject_memory_context
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")