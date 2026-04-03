# tools/web.py
# Outils de recherche et fetch web

from langchain_core.tools import tool
import subprocess
import json


@tool
def web_search_tool(query: str, max_results: int = 5) -> str:
    """
    Recherche sur le web et retourne les résultats.
    
    Args:
        query: Requête de recherche
        max_results: Nombre maximum de résultats (défaut: 5)
    
    Returns:
        str: Résultats de recherche formatés
    """
    try:
        # Use curl to call Tavily API or fallback to simple HTTP request
        result = subprocess.run(
            ["curl", "-s", "https://api.tavily.com/search", 
             "-H", "Content-Type: application/json",
             "-d", json.dumps({"query": query, "max_results": max_results})],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0 and result.stdout:
            data = json.loads(result.stdout)
            results = data.get("results", [])
            formatted = []
            for r in results:
                title = r.get("title", "No title")
                url = r.get("url", "")
                content = r.get("content", "")[:200]
                formatted.append(f"- {title}\n  {url}\n  {content}")
            return "\n\n".join(formatted) if formatted else "Aucun résultat trouvé"
        
        return "API non disponible - effectuez une recherche manuelle"
        
    except Exception as e:
        return f"ERREUR recherche web : {str(e)}"


@tool
def web_fetch_tool(url: str, extract_depth: str = "basic") -> str:
    """
    Extrait le contenu d'une URL.
    
    Args:
        url: URL à extraire
        extract_depth: 'basic' ou 'advanced' (non implémenté pour curl)
    
    Returns:
        str: Contenu extrait de la page
    """
    try:
        result = subprocess.run(
            ["curl", "-s", url],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode == 0:
            # Return first 5000 chars
            return result.stdout[:5000]
        
        return f"ERREUR : impossible de récupérer {url}"
        
    except Exception as e:
        return f"ERREUR extraction : {str(e)}"