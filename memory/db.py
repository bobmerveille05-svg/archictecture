# memory/db.py
# Couche base de données SQLite pour la mémoire

import sqlite3
from pathlib import Path
import os


def get_db_path() -> Path:
    """Resolve DB path at call time so env overrides work in tests/runtime."""
    return Path(os.getenv("MEMORY_DB_PATH", "agent_memory.db"))


def get_connection():
    conn = sqlite3.connect(get_db_path())
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Crée les tables si elles n'existent pas."""
    conn = get_connection()
    conn.executescript("""
        -- Couche 1 : profil utilisateur
        CREATE TABLE IF NOT EXISTS profile (
            key        TEXT PRIMARY KEY,
            value      TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );

        -- Couche 2 : journal de travail
        CREATE TABLE IF NOT EXISTS journal (
            id         INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            objective  TEXT NOT NULL,
            steps      TEXT NOT NULL,   -- JSON
            outcome    TEXT NOT NULL,
            learned    TEXT,
            created_at TEXT NOT NULL
        );

        -- Couche 3 : sessions actives (reprise de tâche)
        CREATE TABLE IF NOT EXISTS sessions (
            session_id TEXT PRIMARY KEY,
            state_json TEXT NOT NULL,
            updated_at TEXT NOT NULL
        );
    """)
    conn.commit()
    conn.close()
