"""dooma mock — random timed mock interview session."""

from __future__ import annotations

import random
import time
import webbrowser

import typer
from rich.prompt import Prompt

from dooma import db, display
from dooma.loader import load_index
from dooma.display import console

app = typer.Typer(help="Timed mock interview session.")


def run_mock(count: int = 5, difficulty: str = ""):
    """Core mock logic — callable from menu or CLI."""
    index = load_index()
    pool = list(index.questions.values())

    if difficulty:
        pool = [q for q in pool if q.difficulty == difficulty.lower()]

    if len(pool) < count:
        console.print(f"[red]Not enough questions ({len(pool)} available, {count} requested)[/red]")
        return

    selected = random.sample(pool, count)
    start_time = time.time()

    console.clear()
    console.print(display.render_logo())
    console.print(f"\n[bold #F39C12]🎯 Mock Interview — {count} Questions[/bold #F39C12]")
    console.print("[dim]Timer starts now. Press Enter after each question to continue.[/dim]\n")

    for i, q in enumerate(selected, 1):
        dc = display.difficulty_color(q.difficulty)
        console.print(f"[bold]Q{i}/{count}[/bold]  [{dc}]{q.difficulty or 'N/A'}[/{dc}]  {q.title}")
        console.print(f"  [blue]{q.url}[/blue]")

        action = Prompt.ask("[dim]Enter to continue, o to open, m to mark solved, s to skip[/dim]", default="")
        if action == "o" and q.url:
            webbrowser.open(q.url)
        elif action == "m":
            db.set_status(q.id, "solved")
            db.increment_streak_today()
            console.print("[green]  ✅ Marked solved[/green]")
        elif action == "s":
            db.set_status(q.id, "skipped")

    elapsed = time.time() - start_time
    minutes = int(elapsed // 60)
    seconds = int(elapsed % 60)
    console.print(f"\n[bold #F39C12]⏱️  Session complete in {minutes}m {seconds}s[/bold #F39C12]")
    console.print(f"[dim]Questions attempted: {count}[/dim]")


@app.callback(invoke_without_command=True)
def mock(
    count: int = typer.Option(5, help="Number of questions"),
    difficulty: str = typer.Option("", help="Filter by difficulty"),
):
    """Start a random timed mock interview session."""
    run_mock(count=count, difficulty=difficulty)
