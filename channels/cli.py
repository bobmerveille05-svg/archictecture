# channels/cli.py
# CLI interface with Typer and Rich.

import uuid

import typer
from rich.console import Console
from rich.panel import Panel

from core.graph import build_graph
from memory.db import init_db

app = typer.Typer(help="Local agent - Hermes/OpenClaw style")
console = Console()


@app.command()
def run(
    objective: str = typer.Argument(..., help="Objective to execute"),
    session_id: str = typer.Option(None, help="Session ID for resume"),
    verbose: bool = typer.Option(False, "--verbose", "-v"),
):
    """Run the agent on an objective."""
    init_db()
    graph = build_graph()

    sid = session_id or str(uuid.uuid4())
    console.print(
        Panel(
            f"[bold cyan]Objective:[/bold cyan] {objective}\n"
            f"[dim]Session: {sid}[/dim]",
            title="Agent",
            border_style="cyan",
        )
    )

    config = {"configurable": {"thread_id": sid}}
    inputs = {
        "objective": objective,
        "messages": [],
        "plan": [],
        "current_step": 0,
        "tool_results": [],
        "decision": "",
        "decision_reason": "",
        "iteration": 0,
        "retry_count": 0,
        "max_retries": 2,
        "max_iterations": 20,
        "memory_context": "",
        "errors": [],
    }

    try:
        with console.status("[bold green]Agent is running...[/bold green]"):
            for step_output in graph.stream(inputs, config=config):
                node_name = list(step_output.keys())[0]
                node_data = step_output[node_name]

                if verbose:
                    console.print(f"[dim]node: {node_name}[/dim]")

                if node_name == "plan" and node_data.get("plan"):
                    console.print("\n[bold yellow]Plan:[/bold yellow]")
                    for i, step in enumerate(node_data["plan"], 1):
                        console.print(f"  {i}. {step}")

                if node_name == "record_result":
                    results = node_data.get("tool_results", [])
                    if results:
                        last_result = results[-1]
                        status = "OK" if last_result.get("success") else "ERR"
                        color = "green" if status == "OK" else "red"
                        snippet = (last_result.get("output") or "")[:200]
                        console.print(f"\n[{color}]{status}[/{color}] {snippet}")

                if node_name == "decide":
                    decision = node_data.get("decision")
                    if decision == "finish":
                        console.print("\n[bold green]Task completed[/bold green]")
                    elif decision == "error":
                        console.print("\n[bold red]Blocking error detected[/bold red]")
    except KeyboardInterrupt:
        console.print("\n[yellow]Interrupted - session can be resumed.[/yellow]")
        console.print(f"[dim]Resume with: agent run --session-id {sid} \"...\"[/dim]")


@app.command()
def resume(
    session_id: str = typer.Argument(..., help="Session ID to resume"),
):
    """Resume an interrupted session."""
    console.print(f"[cyan]Resuming session {session_id}...[/cyan]")
    graph = build_graph()
    config = {"configurable": {"thread_id": session_id}}

    for step_output in graph.stream(None, config=config):
        node_name = list(step_output.keys())[0]
        console.print(f"[dim]{node_name}[/dim]")

    console.print("[green]Session resumed.[/green]")


@app.command()
def history(
    query: str = typer.Argument("", help="Search query for past sessions"),
):
    """Display session history."""
    from memory.journal import search_journal

    init_db()
    results = search_journal(query, limit=10)
    if not results:
        console.print("[dim]No sessions found.[/dim]")
        return

    for item in results:
        console.print(
            Panel(
                f"[yellow]{item['objective']}[/yellow]\n"
                f"[green]Outcome:[/green] {item['outcome'][:200]}\n"
                f"[cyan]Learned:[/cyan] {item.get('learned', '') or '-'}",
                title=f"{item['created_at'][:10]}",
                border_style="dim",
            )
        )


if __name__ == "__main__":
    app()
