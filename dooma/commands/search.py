"""dooma search — fuzzy search across all questions."""

from __future__ import annotations

import typer
from rich.prompt import Prompt

from dooma import db, display
from dooma.loader import load_index
from dooma.search import fuzzy_search
from dooma.display import console

app = typer.Typer(help="Search questions by keyword.")


@app.callback(invoke_without_command=True)
def search(
    query: str = typer.Argument("", help="Search query"),
    limit: int = typer.Option(20, help="Max results"),
):
    """Fuzzy search across question titles, patterns, and topics."""
    index = load_index()

    if not query:
        query = Prompt.ask("[bold]Search[/bold]")

    if not query.strip():
        console.print("[dim]Empty query.[/dim]")
        raise typer.Exit(0)

    results = fuzzy_search(query, index, limit=limit)
    if not results:
        console.print(f"[red]No results for '{query}'[/red]")
        raise typer.Exit(0)

    statuses = db.get_all_statuses()
    table = display.render_question_table(results, title=f"Search: {query}", statuses=statuses)
    console.print(table)
