"""dooma search — fuzzy search across all questions."""

from __future__ import annotations

import typer
from rich.prompt import Prompt

from dooma.display import console
from dooma.loader import load_index
from dooma.search import fuzzy_search

app = typer.Typer(help="Search questions by keyword.")


@app.callback(invoke_without_command=True)
def search_interactive():
    """Interactive search prompt (used from dooma home screen)."""
    index = load_index()
    query = Prompt.ask("[bold]Search[/bold]")
    if not query.strip():
        console.print("[dim]Empty query.[/dim]")
        raise typer.Exit(0)
    results = fuzzy_search(query, index)
    if not results:
        console.print(f"[red]No results for '{query}'[/red]")
        raise typer.Exit(0)
    from dooma import db, display
    statuses = db.get_all_statuses()
    table = display.render_question_table(results, title=f"Search: {query}", statuses=statuses)
    console.print(table)
