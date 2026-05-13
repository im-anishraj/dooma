"""Dooma CLI — main Typer application with all command registrations."""

from __future__ import annotations

import webbrowser

import typer
from rich.prompt import Prompt
from rich.table import Table

from dooma import __version__, db, display
from dooma.commands.browse import app as browse_app
from dooma.commands.dashboard import app as dashboard_app
from dooma.commands.mock import app as mock_app
from dooma.commands.practice import app as practice_app
from dooma.commands.search import app as search_app
from dooma.commands.sheet import app as sheet_app
from dooma.config import is_onboarded, save_config
from dooma.display import console, render_logo, show_onboarding
from dooma.loader import load_index
from dooma.search import fuzzy_search

app = typer.Typer(
    name="dooma",
    help="Dooma — your ultimate DSA interview preparation companion.",
    add_completion=False,
    no_args_is_help=False,
)

# Register sub-commands
app.add_typer(practice_app, name="practice")
app.add_typer(browse_app, name="browse")
app.add_typer(search_app, name="search")
app.add_typer(sheet_app, name="sheet")
app.add_typer(mock_app, name="mock")
app.add_typer(dashboard_app, name="dashboard")


@app.command()
def version():
    """Print version and exit."""
    console.print(f"dooma {__version__}")


@app.command()
def question(slug: str = typer.Argument(..., help="Question slug (e.g. two-sum)")):
    """Open a specific question by slug."""
    index = load_index()
    q = index.questions.get(slug)
    if not q:
        console.print(f"[red]Question '{slug}' not found.[/red]")
        raise typer.Exit(1)

    dc = display.difficulty_color(q.difficulty)
    st = db.get_status(q.id)
    bm = " 📌" if db.is_bookmarked(q.id) else ""
    console.print(f"\n[bold]{q.title}[/bold]{bm}")
    console.print(f"  Difficulty: [{dc}]{q.difficulty or 'N/A'}[/{dc}]")
    console.print(f"  Status: {display.status_icon(st)} {st}")
    console.print(f"  URL: [blue]{q.url}[/blue]")
    if q.patterns:
        console.print(f"  Patterns: {', '.join(q.patterns)}")
    if q.companies:
        top_companies = sorted(q.companies.items(), key=lambda x: x[1].get("frequency", 0), reverse=True)[:5]
        console.print(f"  Top companies: {', '.join(c for c, _ in top_companies)}")

    note = db.get_note(q.id)
    if note:
        console.print(f"  Note: {note}")

    console.print("\n[dim]o: open in browser • m: cycle status • b: bookmark • q: quit[/dim]")
    action = Prompt.ask("Action", default="q")
    if action == "o" and q.url:
        webbrowser.open(q.url)
    elif action == "m":
        cycle = ["unsolved", "attempted", "solved", "skipped"]
        cur = cycle.index(st) if st in cycle else 0
        new_st = cycle[(cur + 1) % len(cycle)]
        db.set_status(q.id, new_st)
        console.print(f"[green]Status → {new_st}[/green]")
    elif action == "b":
        result = db.toggle_bookmark(q.id)
        console.print(f"[green]{'Bookmarked' if result else 'Unbookmarked'}[/green]")


@app.command("config")
def config_cmd(
    reset: bool = typer.Option(False, "--reset", help="Reset configuration"),
):
    """Manage Dooma configuration."""
    if reset:
        from dooma.config import reset_config
        reset_config()
        console.print("[green]Config reset. Onboarding will run on next launch.[/green]")
    else:
        from dooma.config import load_config
        cfg = load_config()
        for k, v in cfg.items():
            console.print(f"  {k}: {v}")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    """Dooma home — interactive DSA prep hub."""
    if ctx.invoked_subcommand is not None:
        return

    # Onboarding
    if not is_onboarded():
        answers = show_onboarding()
        save_config(answers)

    try:
        index = load_index()
        while True:
            console.clear()
            logo = render_logo()
            welcome = f"[bold #F39C12]Dooma v{__version__} — DSA Interview Prep[/bold #F39C12]"

            grid = Table.grid(padding=(0, 2))
            grid.add_column(justify="center", vertical="middle")
            grid.add_column(justify="left", vertical="middle")
            grid.add_row(logo, welcome)
            console.print(grid)

            console.print("\n[bold #E74C3C]Commands:[/bold #E74C3C]")
            menu = [
                ("1", "practice", "Pattern-first question browser"),
                ("2", "browse", "Browse patterns & companies"),
                ("3", "search", "Fuzzy search questions"),
                ("4", "sheet", "Curated roadmaps"),
                ("5", "mock", "Timed mock interview"),
                ("6", "dashboard", "Your progress stats"),
                ("q", "quit", "Exit Dooma"),
            ]
            for key, cmd, desc in menu:
                console.print(f"  [bold #F7CA18]{key}[/bold #F7CA18]  {cmd:<12} [dim]{desc}[/dim]")

            choice = Prompt.ask("\nYour choice", default="q")
            choice = choice.strip().lower()

            if choice in ("q", "0"):
                console.print("[bold #F39C12]Goodbye! 🚀[/bold #F39C12]")
                raise typer.Exit(0)
            elif choice in ("1", "practice"):
                from dooma.commands.practice import run_practice
                run_practice()
            elif choice in ("2", "browse"):
                from dooma.commands.browse import _browse_companies
                _browse_companies()
            elif choice in ("3", "search"):
                q = Prompt.ask("[bold]Search query[/bold]", default="")
                if q:
                    results = fuzzy_search(q, index)
                    statuses = db.get_all_statuses()
                    table = display.render_question_table(results, title=f"Search: {q}", statuses=statuses)
                    console.print(table)
                    Prompt.ask("Press Enter to continue")
            elif choice in ("4", "sheet"):
                from dooma.commands.sheet import run_sheet
                run_sheet()
            elif choice in ("5", "mock"):
                from dooma.commands.mock import run_mock
                run_mock()
            elif choice in ("6", "dashboard"):
                from dooma.commands.dashboard import dashboard as dash_cmd
                dash_cmd()
                Prompt.ask("\nPress Enter to continue")
    except KeyboardInterrupt:
        console.print("\n[bold #F39C12]Goodbye! 🚀[/bold #F39C12]")
        raise typer.Exit(0)


if __name__ == "__main__":
    app()
