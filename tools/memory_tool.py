# tools/memory_tool.py
# Outils de lecture/écriture dans la mémoire

from langchain_core.tools import tool
from memory.profile import set_profile, get_profile, get_all_profile
from memory.journal import save_session_outcome, search_journal


@tool
def memory_read_tool(key: str = None) -> str:
    """
    Lit les informations de la mémoire.
    
    Args:
        key: Clé spécifique à lire (optionnel). 
             Si None, retourne tout le profil.
    
    Returns:
        str: Valeur stockée ou profil complet
    """
    if key is None:
        profile = get_all_profile()
        if not profile:
            return "Aucun profil enregistré."
        return "\n".join(f"- {k}: {v}" for k, v in profile.items())
    
    value = get_profile(key)
    return value if value else f"Aucune donnée pour la clé: {key}"


@tool
def memory_write_tool(key: str, value: str) -> str:
    """
    Écrit une information dans la mémoire (profil).
    
    Args:
        key: Clé à enregistrer
        value: Valeur à stocker
    
    Returns:
        str: Confirmation de l'enregistrement
    """
    try:
        set_profile(key, value)
        return f"OK : '{key}' enregistré dans la mémoire"
    except Exception as e:
        return f"ERREUR : {str(e)}"


@tool
def memory_search_tool(query: str, limit: int = 5) -> str:
    """
    Recherche dans les sessions passées.
    
    Args:
        query: Terme de recherche
        limit: Nombre de résultats (défaut: 5)
    
    Returns:
        str: Résultats de recherche dans le journal
    """
    results = search_journal(query, limit)
    if not results:
        return "Aucune session similaire trouvée."
    
    formatted = []
    for r in results:
        formatted.append(
            f"[{r['created_at'][:10]}] {r['objective']} → {r['outcome'][:100]}"
        )
    return "\n".join(formatted)