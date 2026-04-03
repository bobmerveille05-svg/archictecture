# core/schemas.py
# Schemas types pour l'agent V2

from typing import TypedDict, Optional, Any, Literal


class ToolCallProposal(TypedDict, total=False):
    """Ce que le LLM propose comme action."""
    tool_name: str
    arguments: dict[str, Any]
    reason: str


class ToolResult(TypedDict):
    """Resultat REEL d'un outil execute par le runtime."""
    tool_name: str
    success: bool
    input: dict[str, Any]
    output: str
    error: Optional[str]
    metadata: dict[str, Any]
    recoverable: bool


class PlanStep(TypedDict):
    """Une etape du plan."""
    index: int
    description: str
    status: Literal["pending", "in_progress", "completed", "failed"]
    result: Optional[ToolResult]


class SessionSummary(TypedDict):
    """Resume de la session pour la memoire."""
    objective: str
    steps_completed: int
    total_steps: int
    outcome: str
    learned: str