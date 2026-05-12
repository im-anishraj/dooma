"""dooma dashboard — progress statistics."""

from __future__ import annotations

import typer

from dooma import db, display
from dooma.loader import load_index
from dooma.display import console

app = typer.Typer(help="View your progress dashboard.")


@app.callback(invoke_without_command=True)
def dashboard():
    """Show progress stats, streaks, and bookmarks."""
    index = load_index()
    stats = db.get_dashboard_stats()
    stats["total_questions"] = len(index.questions)

    console.clear()
    console.print(display.render_logo())
    console.print()
    console.print(display.render_dashboard(stats))
    console.print(f"\n[dim]Total questions in database: {stats['total_questions']}[/dim]")
