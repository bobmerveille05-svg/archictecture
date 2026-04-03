# core/nodes.py
# Les 6 noeuds LangGraph V2 - Runtime-centric
# Principe: runtime keep control, LLM propose

from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage
from core.state import AgentState
from core.schemas import ToolCallProposal, ToolResult
from core.prompts import PLAN_PROMPT, ACT_PROMPT
from tools import get_tools_executor
from observability.logger import log_action
import os
import json
from datetime import datetime, timezone


# Configuration du LLM
llm = ChatOpenAI(
    model=os.getenv("MODEL_NAME", "gpt-4o"),
    temperature=0,
    api_key=os.getenv("OPENAI_API_KEY", "")
)

# LLM bindé avec les outils
llm_with_tools = llm.bind_tools(get_tools_executor())


# ═══════════════════════════════════════════════════════════════════════════════
# NOEUD 1: PLAN - Cree ou ajuste le plan
# ═══════════════════════════════════════════════════════════════════════════════

def plan_node(state: AgentState) -> dict:
    """Cree ou ajuste le plan. S'execute une seule fois si plan deja present."""
    if state.get("plan"):
        return {}

    context = state.get("memory_context", "")

    response = llm.invoke([
        SystemMessage(content=PLAN_PROMPT.format(context=context)),
        HumanMessage(content=state["objective"]),
    ])

    steps = [
        line.strip()
        for line in response.content.strip().split("\n")
        if line.strip() and line.strip()[0].isdigit()
    ]

    log_action("plan", {"steps": steps, "objective": state["objective"]})

    return {
        "plan": steps,
        "current_step": 0,
        "status": "running",
        "decision": "execute",
        "decision_reason": "Plan cree",
        "iteration": 0,
        "retry_count": 0,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# NOEUD 2: CHOOSE_ACTION - LLM propose une action
# ═══════════════════════════════════════════════════════════════════════════════

def choose_action_node(state: AgentState) -> dict:
    """Le LLM propose une action. NE FAIT QUE PROPOSER - pas d'execution."""
    plan = state["plan"]
    step_i = state["current_step"]
    
    if step_i >= len(plan):
        return {
            "status": "finished",
            "decision": "finish",
            "decision_reason": "Toutes etapes terminees",
            "session_summary": f"Termine: {step_i}/{len(plan)} etapes",
        }

    current_step = plan[step_i]
    context = state.get("memory_context", "")
    
    tool_results = state.get("tool_results", [])
    results_text = ""
    if tool_results:
        results_text = "\n\n--- Resultats precedents ---\n"
        for r in tool_results[-3:]:
            status = "OK" if r["success"] else "ECHEC"
            results_text += f"[{status}] {r['tool_name']}: {r['output'][:200]}\n"
            if r.get("error"):
                results_text += f"  Erreur: {r['error']}\n"

    response = llm_with_tools.invoke([
        SystemMessage(content=ACT_PROMPT.format(context=context, observations=results_text)),
        HumanMessage(content=f"Etape {step_i + 1}/{len(plan)}: {current_step}"),
    ])

    proposal: ToolCallProposal = {"tool_name": "", "arguments": {}, "reason": ""}
    
    if response.tool_calls:
        tc = response.tool_calls[0]
        proposal["tool_name"] = tc.name
        proposal["arguments"] = tc.args if isinstance(tc.args, dict) else {}
        proposal["reason"] = f"Propose par LLM pour: {current_step}"
    else:
        proposal["tool_name"] = "noop"
        proposal["arguments"] = {"content": response.content}
        proposal["reason"] = "Reponse directe du LLM"

    log_action("choose_action", {"step": step_i, "proposal": proposal["tool_name"]})

    return {
        "messages": [response],
        "last_proposal": proposal,
        "iteration": state.get("iteration", 0) + 1,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# NOEUD 3: EXECUTE_TOOL - Runtime execute reellement l'outil
# ═══════════════════════════════════════════════════════════════════════════════

def execute_tool_node(state: AgentState) -> dict:
    """Execute REALEMENT les outils. Le runtime execute, pas le LLM."""
    proposal = state.get("last_proposal", {})
    tool_name = proposal.get("tool_name", "")
    tool_args = proposal.get("arguments", {})
    
    if not tool_name or tool_name == "noop":
        return {
            "last_result": {
                "tool_name": "noop",
                "success": True,
                "input": tool_args,
                "output": tool_args.get("content", ""),
                "error": None,
                "metadata": {},
                "recoverable": False,
            },
            "decision": "next_step",
            "decision_reason": "Reponse directe, pas d'outil necessaire",
        }
    
    tools_map = {t.name: t for t in get_tools_executor()}
    tool_func = tools_map.get(tool_name)
    
    if not tool_func:
        return {
            "last_result": {
                "tool_name": tool_name,
                "success": False,
                "input": tool_args,
                "output": "",
                "error": f"Outil '{tool_name}' non trouve",
                "metadata": {},
                "recoverable": False,
            },
            "decision": "error",
            "decision_reason": "Outil non trouve",
        }
    
    log_action("execute_tool", {"tool": tool_name, "args": str(tool_args)[:200]})
    
    try:
        if isinstance(tool_args, dict):
            result = tool_func.invoke(tool_args)
        else:
            try:
                args_dict = json.loads(tool_args) if isinstance(tool_args, str) else {}
                result = tool_func.invoke(args_dict)
            except:
                result = tool_func.invoke(tool_args)
        
        return {
            "last_result": {
                "tool_name": tool_name,
                "success": True,
                "input": tool_args,
                "output": str(result)[:2000],
                "error": None,
                "metadata": {"timestamp": datetime.now(timezone.utc).isoformat()},
                "recoverable": False,
            },
            "decision": "next_step",
            "decision_reason": f"Execution reussie: {tool_name}",
        }
    except Exception as e:
        error_msg = str(e)[:500]
        recoverable = any(kw in error_msg.lower() for kw in ["permission", "chemin", "timeout"])
        
        return {
            "last_result": {
                "tool_name": tool_name,
                "success": False,
                "input": tool_args,
                "output": "",
                "error": error_msg,
                "metadata": {"timestamp": datetime.now(timezone.utc).isoformat()},
                "recoverable": recoverable,
            },
            "decision": "error" if not recoverable else "replan",
            "decision_reason": f"Erreur: {error_msg[:100]}",
        }


# ═══════════════════════════════════════════════════════════════════════════════
# NOEUD 4: RECORD_RESULT - Normalise le resultat + logs
# ═══════════════════════════════════════════════════════════════════════════════

def record_result_node(state: AgentState) -> dict:
    """Normalise le resultat et l'ajoute a l'historique. La verite est stockee ici."""
    last_result = state.get("last_result")
    
    if not last_result:
        return {}
    
    log_action("record_result", {
        "tool": last_result.get("tool_name"),
        "success": last_result.get("success"),
        "output_len": len(last_result.get("output", "")),
    })

    # AgentState.tool_results uses operator.add aggregator in LangGraph.
    # Return only the delta to avoid duplicating historical entries.
    return {"tool_results": [last_result]}


# ═══════════════════════════════════════════════════════════════════════════════
# NOEUD 5: DECIDE - Decision RUNTIME (pas LLM)
# ═══════════════════════════════════════════════════════════════════════════════

def decide_node(state: AgentState) -> dict:
    """
    Decision RUNTIME en premier. Logique:
    1. Si erreur bloquante -> error
    2. Si max iterations -> error
    3. Si toutes etapes terminees -> finish
    4. Si erreur recuperable -> replan
    5. Si succes -> next_step
    """
    max_iterations = state.get("max_iterations", int(os.getenv("MAX_ITERATIONS", "20")))
    max_retries = state.get("max_retries", int(os.getenv("MAX_RETRIES", "2")))
    retry_count = state.get("retry_count", 0)
    iteration = state.get("iteration", 0)
    
    if iteration >= max_iterations:
        return {
            "status": "error",
            "decision": "error",
            "decision_reason": f"Max iterations atteint ({max_iterations})",
            "session_summary": f"Erreur: max iterations ({iteration}/{max_iterations})",
            "errors": [f"Max iterations: {max_iterations}"],
        }
    
    plan = state["plan"]
    step_i = state["current_step"]
    
    if step_i >= len(plan):
        return {
            "status": "finished",
            "decision": "finish",
            "decision_reason": "Toutes les etapes terminees",
            "session_summary": f"Succes: {step_i}/{len(plan)} etapes completes",
        }
    
    last_result = state.get("last_result")
    
    if not last_result:
        return {"decision": "execute", "decision_reason": "Premiere iteration"}
    
    if not last_result["success"]:
        error_msg = last_result.get("error", "") or ""
        
        if last_result.get("recoverable", False) and retry_count < max_retries:
            return {
                "decision": "replan",
                "decision_reason": f"Erreur recuperable: {error_msg[:50]}",
                "retry_count": retry_count + 1,
            }
        
        return {
            "status": "error",
            "decision": "error",
            "decision_reason": f"Erreur bloquante: {error_msg[:50]}",
            "session_summary": f"Erreur: {error_msg[:100]}",
            "errors": [error_msg],
        }
    
    return {
        "decision": "next_step",
        "decision_reason": f"Succes: {last_result['tool_name']}",
        "current_step": step_i + 1,
    }


# ═══════════════════════════════════════════════════════════════════════════════
# NOMS DES NOEUDS
# ═══════════════════════════════════════════════════════════════════════════════

PLAN_NODE = "plan"
CHOOSE_ACTION_NODE = "choose_action"
EXECUTE_TOOL_NODE = "execute_tool"
RECORD_RESULT_NODE = "record_result"
DECIDE_NODE = "decide"
