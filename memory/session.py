# memory/session.py
# Couche 3 : injection de contexte mémoire

# Import de type différé pour éviter circular import
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from core.state import AgentState

from memory.profile import get_all_profile
from memory.journal import search_journal


def inject_memory_context(state: "AgentState") -> dict:
    """
    Nœud LangGraph : injecte la mémoire pertinente
    dans le contexte avant chaque tour.
    """
    objective = state.get("objective", "")

    # profil complet de l'utilisateur
    profile = get_all_profile()
    profile_text = "\n".join(
        f"- {k}: {v}" for k, v in profile.items()
    ) or "Aucun profil enregistré."

    # journaux de sessions similaires passées
    past = search_journal(objective[:50], limit=3)
    past_text = "\n".join(
        f"[{r['created_at'][:10]}] {r['objective']} → {r['outcome']}"
        for r in past
    ) or "Aucune session similaire trouvée."

    context = f"""
=== PROFIL UTILISATEUR ===
{profile_text}

=== SESSIONS PASSÉES SIMILAIRES ===
{past_text}
""".strip()

    return {"memory_context": context}