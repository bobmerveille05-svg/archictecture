# tools/registry.py
# Registry centralise des outils disponibles

from typing import Callable
from langchain_core.tools import BaseTool


class ToolRegistry:
    """
    Registry centralise pour tous les outils de l'agent.
    Permet validation et安全管理 des outils.
    """
    
    def __init__(self):
        self._tools: dict[str, BaseTool] = {}
        self._tool_functions: dict[str, Callable] = {}
    
    def register(self, tool: BaseTool) -> None:
        """Enregistre un outil dans le registry."""
        self._tools[tool.name] = tool
        self._tool_functions[tool.name] = tool.func
    
    def get(self, name: str) -> BaseTool | None:
        """Retourne un outil par son nom."""
        return self._tools.get(name)
    
    def get_function(self, name: str) -> Callable | None:
        """Retourne la fonction d'un outil."""
        return self._tool_functions.get(name)
    
    def list_tools(self) -> list[str]:
        """Liste tous les noms d'outils disponibles."""
        return list(self._tools.keys())
    
    def is_registered(self, name: str) -> bool:
        """Verifie si un outil est enregistre."""
        return name in self._tools
    
    def execute(self, tool_name: str, arguments: dict) -> dict:
        """
        Execute un outil avec ses arguments.
        Retourne un resultat structure.
        """
        tool_func = self.get_function(tool_name)
        if not tool_func:
            return {
                "success": False,
                "error": f"Outil '{tool_name}' non trouve",
                "output": "",
            }
        
        try:
            result = tool_func.invoke(arguments)
            return {
                "success": True,
                "output": str(result)[:2000],
                "error": None,
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)[:500],
                "output": "",
            }


# Instance globale du registry
_registry = ToolRegistry()


def get_registry() -> ToolRegistry:
    """Retourne l'instance globale du registry."""
    return _registry


def register_tool(tool: BaseTool) -> None:
    """Enregistre un outil dans le registry global."""
    _registry.register(tool)