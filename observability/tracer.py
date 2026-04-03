# observability/tracer.py
# Traçage optionnel pour LangSmith ou autre

import os
from typing import Optional


def get_tracer() -> Optional[any]:
    """
    Retourne un traceur configuré (LangSmith ou autre).
    Optionnel : désactivé si pas de configuration.
    """
    langsmith_api_key = os.getenv("LANGSMITH_API_KEY", "")
    langsmith_project = os.getenv("LANGSMITH_PROJECT", "agent")

    if not langsmith_api_key:
        return None

    try:
        from langsmith import Client
        return Client(
            api_key=langsmith_api_key,
            project=langsmith_project,
        )
    except ImportError:
        return None


def trace_run(name: str, metadata: dict = None):
    """
    Décorateur/context manager pour tracer les runs.
    À utiliser avec LangGraph si activé.
    """
    tracer = get_tracer()
    if tracer is None:
        # Pas de tracing - return no-op context manager
        from contextlib import nullcontext
        return nullcontext()

    # Implementation depends on langsmith SDK
    # This is a placeholder for actual implementation
    from contextlib import nullcontext
    return nullcontext()