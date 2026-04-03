# tools/files.py
# Outils de lecture/écriture de fichiers

from pathlib import Path
from langchain_core.tools import tool
from sandbox.permissions import check_permission, normalize_path
import os

# Base directory pour les fichiers
ALLOWED_BASE = os.getenv("SANDBOX_DIR", "/tmp/agent")


@tool
def read_file_tool(path: str) -> str:
    """Lit un fichier dans la zone autorisee."""
    # Normaliser le chemin - accepte relatif ou absolu
    full_path = normalize_path(path, ALLOWED_BASE)
    
    # Verifier permission via le sandbox
    if not check_permission("read", str(full_path)):
        return f"BLOQUE : chemin non autorise -> {path}"

    try:
        if not full_path.exists():
            return f"ERREUR : fichier introuvable -> {path}"
        
        content = full_path.read_text(encoding="utf-8")
        return content[:5000]  # Tronquer pour eviter overflow
        
    except IsADirectoryError:
        return f"ERREUR : {path} est un repertoire"
    except PermissionError:
        return f"ERREUR : permission refusee -> {path}"
    except Exception as e:
        return f"ERREUR : {str(e)}"


@tool
def write_file_tool(path: str, content: str) -> str:
    """Ecrit un fichier dans la zone autorisee."""
    # Normaliser le chemin - accepte relatif ou absolu
    full_path = normalize_path(path, ALLOWED_BASE)

    # Verifier permission via le sandbox
    if not check_permission("write", str(full_path)):
        return f"BLOQUE : chemin non autorise -> {path}"

    try:
        # Creer les dossiers parents si necessaires
        full_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Ecrire le fichier
        full_path.write_text(content, encoding="utf-8")
        return f"OK : fichier ecrit -> {path}"
        
    except PermissionError:
        return f"ERREUR : permission refusee -> {path}"
    except Exception as e:
        return f"ERREUR : {str(e)}"


@tool
def list_directory_tool(path: str = "") -> str:
    """Liste les fichiers d'un repertoire."""
    target = path if path else ALLOWED_BASE
    full_path = normalize_path(target, ALLOWED_BASE)
    
    if not check_permission("read", str(full_path)):
        return f"BLOQUE : chemin non autorise -> {path}"

    try:
        if not full_path.exists():
            return f"ERREUR : repertoire introuvable -> {path}"
        
        if not full_path.is_dir():
            return f"ERREUR : pas un repertoire -> {path}"
        
        items = []
        for item in sorted(full_path.iterdir()):
            prefix = "d" if item.is_dir() else "f"
            name = item.name
            size = item.stat().st_size if item.is_file() else 0
            items.append(f"{prefix} {name} ({size} bytes)")
        
        return "\n".join(items) if items else "(repertoire vide)"
        
    except Exception as e:
        return f"ERREUR : {str(e)}"