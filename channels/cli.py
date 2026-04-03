# channels/cli.py
# Interface CLI avec Typer et Rich

import typer
from rich.console import Console
from rich.panel import Panel
from rich.spinner import Spinner
from rich.live import Live
from rich import print as rprint
import uuid

from core.graph import build_graph
from memory.db import init_db
from memory.journal import save_session_outcome

app = typer.Typer(help="Agent local — style Hermes/OpenClaw")
console = Console()


@app.command()
def run(
    objective: str = typer.Argument(..., help="Objectif à accomplir"),
    session_id: str = typer.Option(None, help="ID session pour reprise"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """Lance l'agent sur un objectif."""

    init_db()
    graph = build_graph()

    sid = session_id or str(uuid.uuid4())

    console.print(Panel(
        f"[bold cyan]Objectif :[/bold cyan] {objective}\n"
        f"[dim]Session  : {sid}[/dim]",
        title="🤖 Agent",
        border_style="cyan",
    ))

    config = {"configurable": {"thread_id": sid}}
    inputs = {
        "objective": objective,
        "messages": [],
        "plan": [],
        "current_step": 0,
        "observations": [],
        "decision": "",
        "iteration": 0,
        "memory_context": "",
        "errors": [],
    }

    try:
        with console.status("[bold green]Agent en train de réfléchir...[/bold green]"):
            for step_output in graph.stream(inputs, config=config):
                node_name = list(step_output.keys())[0]
                node_data = step_output[node_name]

                if verbose:
                    console.print(f"[dim]→ nœud : {node_name}[/dim]")

                # affiche le plan quand il est créé
                if node_name == "plan" and node_data.get("plan"):
                    console.print("\n[bold yellow]📋 Plan :[/bold yellow]")
                    for i, step in enumerate(node_data["plan"], 1):
                        console.print(f"  {i}. {step}")

                # affiche les observations
                if node_name == "observe":
                    obs = node_data.get("observations", [])
                    if obs:
                        console.print(f"\n[green]✓[/green] {obs[-1][:200]}")

                # affiche la décision finale
                if node_name == "decide":
                    decision = node_data.get("decision")
                    if decision == "finish":
                        console.print("\n[bold green]✅ Tâche terminée[/bold green]")
                    elif decision == "error":
                        console.print("\n[bold red]❌ Erreur détectée[/bold red]")

    except KeyboardInterrupt:
        console.print("\n[yellow]⏸ Interrompu — session sauvegardée, reprise possible.[/yellow]")
        console.print(f"[dim]Reprendre avec : agent run --session-id {sid} \"...[/dim]")


@app.command()
def resume(
    session_id: str = typer.Argument(..., help="ID de session à reprendre"),
):
    """Reprend une session interrompue."""
    console.print(f"[cyan]Reprise de la session {session_id}...[/cyan]")
    graph = build_graph()
    config = {"configurable": {"thread_id": session_id}}

    # LangGraph reprend automatiquement depuis le dernier checkpoint
    for step_output in graph.stream(None, config=config):
        node_name = list(step_output.keys())[0]
        console.print(f"[dim]{node_name}[/dim]")

    console.print("[green]Session reprise avec succès.[/green]")


@app.command()
def history(
    query: str = typer.Argument("", help="Recherche dans les sessions passées"),
):
    """Affiche l'historique des sessions."""
    from memory.journal import search_journal
    init_db()

    results = search_journal(query, limit=10)

    if not results:
        console.print("[dim]Aucune session trouvée.[/dim]")
        return

    for r in results:
        console.print(Panel(
            f"[yellow]{r['objective']}[/yellow]\n"
            f"[green]Résultat :[/green] {r['outcome'][:200]}\n"
            f"[cyan]Appris   :[/cyan] {r.get('learned', '') or '—'}",
            title=f"📅 {r['created_at'][:10]}",
            border_style="dim",
        ))


if __name__ == "__main__":
    app()