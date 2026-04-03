# tools/terminal.py
# Outil d'exécution de commandes shell sécurisées

from langchain_core.tools import tool
from sandbox.executor import execute_command
from observability.logger import log_action


@tool
def terminal_tool(command: str) -> str:
    """
    Exécute une commande shell dans un sandbox sécurisé.
    
    Args:
        command: La commande à exécuter
    
    Returns:
        str: Sortie de la commande ou message d'erreur
    """
    log_action("terminal", {"command": command})
    return execute_command(command)