# tools/tasks.py
# Outils de gestion de projets/tâches

from langchain_core.tools import tool
from typing import Optional, List
import json
import os
from pathlib import Path

TASKS_FILE = Path(os.getenv("TASKS_FILE", "/tmp/agent/tasks.json"))


def load_tasks() -> List[dict]:
    """Charge les tâches depuis le fichier."""
    TASKS_FILE.parent.mkdir(parents=True, exist_ok=True)
    if TASKS_FILE.exists():
        try:
            return json.loads(TASKS_FILE.read_text())
        except:
            return []
    return []


def save_tasks(tasks: List[dict]):
    """Sauvegarde les tâches dans le fichier."""
    TASKS_FILE.write_text(json.dumps(tasks, indent=2))


@tool
def task_list_tool(status: str = None) -> str:
    """
    Liste les tâches du projet.
    
    Args:
        status: Filtrer par statut (todo/in_progress/done). 
                Si None, affiche toutes les tâches.
    
    Returns:
        str: Liste des tâches formatée
    """
    tasks = load_tasks()
    
    if status:
        tasks = [t for t in tasks if t.get("status") == status]
    
    if not tasks:
        return "Aucune tâche trouvée."
    
    formatted = []
    for t in tasks:
        status_emoji = {"todo": "○", "in_progress": "◐", "done": "✓"}.get(t.get("status", "todo"), "○")
        formatted.append(f"{status_emoji} [{t.get('status', 'todo')}] {t.get('title', 'Sans titre')}")
        if t.get("description"):
            formatted.append(f"   └─ {t['description'][:60]}")
    
    return "\n".join(formatted)


@tool
def task_add_tool(title: str, description: str = "") -> str:
    """
    Ajoute une nouvelle tâche.
    
    Args:
        title: Titre de la tâche
        description: Description optionnelle
    
    Returns:
        str: Confirmation de création
    """
    tasks = load_tasks()
    task_id = max([t.get("id", 0) for t in tasks], default=0) + 1
    
    new_task = {
        "id": task_id,
        "title": title,
        "description": description,
        "status": "todo",
    }
    tasks.append(new_task)
    save_tasks(tasks)
    
    return f"OK : tâche #{task_id} créée - {title}"


@tool
def task_update_tool(task_id: int, status: str = None, title: str = None, description: str = None) -> str:
    """
    Met à jour une tâche existante.
    
    Args:
        task_id: ID de la tâche à modifier
        status: Nouveau statut (todo/in_progress/done)
        title: Nouveau titre
        description: Nouvelle description
    
    Returns:
        str: Confirmation de mise à jour
    """
    tasks = load_tasks()
    
    for t in tasks:
        if t.get("id") == task_id:
            if status:
                t["status"] = status
            if title:
                t["title"] = title
            if description:
                t["description"] = description
            save_tasks(tasks)
            return f"OK : tâche #{task_id} mise à jour"
    
    return f"ERREUR : tâche #{task_id} non trouvée"