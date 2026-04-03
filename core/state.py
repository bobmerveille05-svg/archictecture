# core/state.py
# L'etat de l'agent V2 - runtime-centric

from typing import TypedDict, Annotated, Optional, Literal, Any
from langgraph.graph.message import add_messages
import operator

# Import des schemas
from core.schemas import ToolCallProposal, ToolResult, PlanStep


class AgentState(TypedDict, total=False):
    """
    L'etat complet qui circule dans le graphe.
    
    PRINCIPE: Le runtime est source de verite, pas le LLM.
    Ce qui compte = ce qui a ete execute, pas ce qui a ete propose.
    """

    # Objectif utilisateur
    objective: str

    # Plan structure
    plan: list[str]
    current_step: int

    # Contexte memoire injecte
    memory_context: str
    
    # Messages LLM (propositions)
    messages: Annotated[list, add_messages]

    # CE QUE LE LLM A PROPOSE (proposition, pas execution)
    last_proposal: Optional[ToolCallProposal]
    
    # CE QUE LE RUNTIME A REELLEMENT OBTENU (verite)
    last_result: Optional[ToolResult]
    tool_results: Annotated[list, operator.add]
    
    # Statut global
    status: Literal["running", "finished", "error"]
    
    # Decision RUNTIME (prochaine transition)
    decision: Literal["execute", "next_step", "replan", "finish", "error"]
    decision_reason: str

    # Limites
    iteration: int
    max_iterations: int
    retry_count: int
    max_retries: int
    
    # Resume de session (pour journal)
    session_summary: str
    
    # Erreurs accumulatees
    errors: Annotated[list, operator.add]