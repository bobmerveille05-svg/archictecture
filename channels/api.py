# channels/api.py
# API REST avec FastAPI (phase 3)

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import uuid

app = FastAPI(title="Agent API", version="0.1.0")


class AgentRequest(BaseModel):
    objective: str
    session_id: Optional[str] = None


class AgentResponse(BaseModel):
    session_id: str
    status: str
    result: Optional[dict] = None


@app.post("/run", response_model=AgentResponse)
async def run_agent(request: AgentRequest):
    """
    Lance l'agent sur un objectif via API REST.
    Phase 3 : implémentation complète avec streaming.
    """
    sid = request.session_id or str(uuid.uuid4())
    
    # Placeholder - implémentation complète en phase 3
    return AgentResponse(
        session_id=sid,
        status="not_implemented",
        result={"message": "API en développement - Phase 3"}
    )


@app.get("/status/{session_id}")
async def get_status(session_id: str):
    """Retourne le statut d'une session."""
    # Placeholder
    return {"session_id": session_id, "status": "unknown"}


@app.get("/history")
async def get_history(query: str = ""):
    """Retourne l'historique des sessions."""
    from memory.journal import search_journal
    results = search_journal(query, limit=20)
    return {"sessions": results}