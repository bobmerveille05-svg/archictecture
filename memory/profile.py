# memory/profile.py
# Couche 1 : profil utilisateur

from memory.db import get_connection
from datetime import datetime


def set_profile(key: str, value: str):
    """Enregistre une info sur l'utilisateur."""
    conn = get_connection()
    conn.execute("""
        INSERT OR REPLACE INTO profile (key, value, updated_at)
        VALUES (?, ?, ?)
    """, (key, value, datetime.utcnow().isoformat()))
    conn.commit()
    conn.close()


def get_profile(key: str) -> str | None:
    conn = get_connection()
    row = conn.execute(
        "SELECT value FROM profile WHERE key = ?", (key,)
    ).fetchone()
    conn.close()
    return row["value"] if row else None


def get_all_profile() -> dict:
    conn = get_connection()
    rows = conn.execute("SELECT key, value FROM profile").fetchall()
    conn.close()
    return {row["key"]: row["value"] for row in rows}