# tools/__init__.py
# Module tools : les mains de l'agent

from tools.terminal import terminal_tool
from tools.files import read_file_tool, write_file_tool, list_directory_tool
from tools.web import web_search_tool, web_fetch_tool
from tools.memory_tool import memory_read_tool, memory_write_tool, memory_search_tool
from tools.tasks import task_list_tool, task_add_tool, task_update_tool


def get_tools_executor() -> list:
    """Retourne la liste de tous les outils disponibles pour le LLM."""
    return [
        terminal_tool,
        read_file_tool,
        write_file_tool,
        list_directory_tool,
        web_search_tool,
        web_fetch_tool,
        memory_read_tool,
        memory_write_tool,
        memory_search_tool,
        task_list_tool,
        task_add_tool,
        task_update_tool,
    ]


__all__ = [
    "terminal_tool",
    "read_file_tool",
    "write_file_tool",
    "list_directory_tool",
    "web_search_tool",
    "web_fetch_tool",
    "memory_read_tool",
    "memory_write_tool",
    "memory_search_tool",
    "task_list_tool",
    "task_add_tool",
    "task_update_tool",
    "get_tools_executor",
]