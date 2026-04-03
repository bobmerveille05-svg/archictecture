# memory/__init__.py
# Module memory : la mémoire de l'agent en 3 couches

from memory.db import init_db, get_connection
from memory.profile import set_profile, get_profile, get_all_profile
from memory.journal import save_session_outcome, search_journal
from memory.session import inject_memory_context

__all__ = [
    "init_db",
    "get_connection",
    "set_profile",
    "get_profile",
    "get_all_profile",
    "save_session_outcome",
    "search_journal",
    "inject_memory_context",
]