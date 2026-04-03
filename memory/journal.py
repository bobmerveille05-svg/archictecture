# memory/journal.py
# Couche 2 : journal de travail

import json
from memory.db import get_connection
from datetime import datetime


def save_session_outcome(
    session_id: str,
    objective: str,
    steps: list[str],
    outcome: str,
    learned: str = "",
):
    """Enregistre ce que l'agent a fait et retenu."""
    conn = get_connection()
    conn.execute("""
        INSERT INTO journal (session_id, objective, steps, outcome, learned, created_at)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        session_id,
        objective,
        json.dumps(steps),
        outcome,
        learned,
        datetime.utcnow().isoformat(),
    ))
    conn.commit()
    conn.close()


def search_journal(query: str, limit: int = 5) -> list[dict]:
    """
    Recherche simple dans les journaux passés.
    (Full-text SQLite, remplacé par vecteurs si besoin plus tard)
    """
    conn = get_connection()
    rows = conn.execute("""
        SELECT objective, outcome, learned, created_at
        FROM journal
        WHERE objective LIKE ? OR outcome LIKE ? OR learned LIKE ?
        ORDER BY created_at DESC
        LIMIT ?
    """, (f"%{query}%", f"%{query}%", f"%{query}%", limit)).fetchall()
    conn.close()
    return [dict(row) for row in rows]