# core/graph.py
# Boucle LangGraph V2 avec 6 noeuds - Runtime-centric
# Principe: runtime keep control, LLM propose

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from core.state import AgentState
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
from memory.session import inject_memory_context
import os


def build_graph(db_path: str = None, use_memory_saver: bool = True) -> StateGraph:
    """
    Construit le graphe LangGraph V2 avec 6 noeuds.
    
    Flux V2 (6 noeuds):
    inject_memory → plan → choose_action → execute_tool → record_result → decide
                                                                        ↑         │
                                                                        └─────────┘
    
    Decisions RUNTIME (pas LLM):
    - execute: meme etape (retry)
    - next_step: passer a l'etape suivante
    - replan: recommencer cette etape avec nouvelle approche
    - finish: termine avec succes
    - error: erreur bloquante
    """
    builder = StateGraph(AgentState)

    # 6 noeuds
    builder.add_node("inject_memory", inject_memory_context)
    builder.add_node(PLAN_NODE, plan_node)
    builder.add_node(CHOOSE_ACTION_NODE, choose_action_node)
    builder.add_node(EXECUTE_TOOL_NODE, execute_tool_node)
    builder.add_node(RECORD_RESULT_NODE, record_result_node)
    builder.add_node(DECIDE_NODE, decide_node)

    # Flux principal
    builder.set_entry_point("inject_memory")
    builder.add_edge("inject_memory", PLAN_NODE)
    builder.add_edge(PLAN_NODE, CHOOSE_ACTION_NODE)
    builder.add_edge(CHOOSE_ACTION_NODE, EXECUTE_TOOL_NODE)
    builder.add_edge(EXECUTE_TOOL_NODE, RECORD_RESULT_NODE)
    builder.add_edge(RECORD_RESULT_NODE, DECIDE_NODE)

    # Branchement conditionnel depuis decide
    builder.add_conditional_edges(
        DECIDE_NODE,
        route_decision,
        {
            "execute": CHOOSE_ACTION_NODE,      # Retry (meme step)
            "next_step": CHOOSE_ACTION_NODE,    # Etape suivante
            "replan": CHOOSE_ACTION_NODE,       # Reessayer avec meme step
            "finish": END,
            "error": END,
        }
    )

    # Persistance
    if use_memory_saver:
        memory = MemorySaver()
        return builder.compile(checkpointer=memory)
    
    try:
        from langgraph_checkpoint_sqlite import SqliteSaver
        memory = SqliteSaver.from_conn_string(f"sqlite:///{db_path or 'agent.db'}")
        return builder.compile(checkpointer=memory)
    except ImportError:
        memory = MemorySaver()
        return builder.compile(checkpointer=memory)


def route_decision(state: AgentState) -> str:
    """Route selon la decision RUNTIME. Le runtime est source de verite."""
    decision = state.get("decision", "error")
    return decision