"""Dooma CLI — main Typer application with all command registrations."""

from __future__ import annotations

import json
import platform
import random as random_module
import sys
import webbrowser
from time import perf_counter

import typer
from rich.align import Align
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

from dooma import __version__, db, display
from dooma.commands.browse import app as browse_app
from dooma.commands.dashboard import app as dashboard_app
from dooma.commands.mock import app as mock_app
from dooma.commands.practice import app as practice_app
from dooma.commands.sheet import app as sheet_app
from dooma.config import get_config_path, is_onboarded, save_config
from dooma.display import console, render_logo, show_onboarding
from dooma.loader import load_index
from dooma.search import fuzzy_search

REPO_URL = "https://github.com/im-anishraj/dooma"
CONTRIBUTING_URL = f"{REPO_URL}/blob/main/CONTRIBUTING.md"
ISSUES_URL = f"{REPO_URL}/issues"

app = typer.Typer(
    name="dooma",
    help="Dooma — your ultimate DSA interview preparation companion.",
    add_completion=False,
    no_args_is_help=False,
)

# Register sub-commands
app.add_typer(practice_app, name="practice")
app.add_typer(browse_app, name="browse")
app.add_typer(sheet_app, name="sheet")
app.add_typer(mock_app, name="mock")
app.add_typer(dashboard_app, name="dashboard")


def _version_callback(value: bool) -> None:
    if value:
        console.print(f"dooma {__version__}", highlight=False)
        raise typer.Exit(0)


@app.command()
def version():
    """Print version and exit."""
    console.print(f"dooma {__version__}", highlight=False)


@app.command("guide")
def guide():
    """Show a practical guide to Dooma's commands, workflows, and support links."""
    console.print(render_logo())
    console.print(
        Panel(
            "[bold #F39C12]Dooma is an offline-first DSA interview prep CLI.[/bold #F39C12]\n"
            "Search questions, browse companies and patterns, work through sheets, "
            "run mock interviews, and track progress locally.",
            border_style="#F39C12",
        )
    )

    commands = Table(title="Essential Commands", show_header=True, header_style="bold #E74C3C")
    commands.add_column("Command", style="#F7CA18", no_wrap=True)
    commands.add_column("Use it for")
    commands.add_row("dooma", "Open the interactive command hub.")
    commands.add_row("dooma guide", "Open this guide.")
    commands.add_row("dooma help", "Alias for dooma guide.")
    commands.add_row("dooma version", "Print the installed version.")
    commands.add_row("dooma search \"two sum\"", "Find questions by fuzzy title/topic search.")
    commands.add_row("dooma question two-sum", "Open a question detail screen.")
    commands.add_row("dooma random --difficulty medium", "Pick a random filtered practice problem.")
    commands.add_row("dooma browse companies", "Browse interactive company question lists.")
    commands.add_row("dooma bookmarks", "Return to saved questions.")
    commands.add_row("dooma dashboard", "View solved, attempted, skipped, notes, and streaks.")
    commands.add_row("dooma doctor", "Check install, dataset, and local state health.")
    console.print(commands)

    actions = Table(title="Question Actions", show_header=True, header_style="bold #E74C3C")
    actions.add_column("Key", style="#F7CA18", no_wrap=True)
    actions.add_column("Action")
    actions.add_row("o", "Open the LeetCode URL in your browser.")
    actions.add_row("m", "Cycle status: unsolved -> attempted -> solved -> skipped.")
    actions.add_row("b", "Bookmark or unbookmark the question.")
    actions.add_row("n", "Add or edit a local note.")
    actions.add_row("q", "Go back.")
    console.print(actions)

    support = Table(title="Support Dooma", show_header=True, header_style="bold #E74C3C")
    support.add_column("Action", style="#F7CA18", no_wrap=True)
    support.add_column("Link")
    support.add_row("Star", REPO_URL)
    support.add_row("Contribute", CONTRIBUTING_URL)
    support.add_row("Issues", ISSUES_URL)
    console.print(support)

    console.print(
        "\n[dim]Progress is stored locally in ~/.dooma/state.db. "
        "The bundled dataset works offline after installation.[/dim]"
    )


@app.command("help")
def help_cmd():
    """Alias for dooma guide."""
    guide()


@app.command("doctor")
def doctor():
    """Check installation, dataset, and local state health."""
    checks: list[tuple[str, str, str]] = []

    checks.append(("Python", platform.python_version(), "OK" if sys.version_info >= (3, 9) else "FAIL"))
    checks.append(("Dooma version", __version__, "OK"))

    start = perf_counter()
    try:
        index = load_index(force=True)
        elapsed = perf_counter() - start
        checks.append(
            (
                "Dataset",
                f"{len(index.questions)} questions, {len(index.companies)} companies in {elapsed:.2f}s",
                "OK",
            )
        )
    except Exception as exc:  # pragma: no cover - defensive health check
        checks.append(("Dataset", str(exc), "FAIL"))

    try:
        conn = db.get_connection()
        conn.execute("SELECT 1").fetchone()
        checks.append(("State database", str(db.get_db_path()), "OK"))
    except Exception as exc:  # pragma: no cover - defensive health check
        checks.append(("State database", str(exc), "FAIL"))

    checks.append(("Config path", str(get_config_path()), "OK"))

    table = Table(title="Dooma Doctor", show_header=True, header_style="bold #E74C3C")
    table.add_column("Check", style="#F7CA18")
    table.add_column("Details")
    table.add_column("Status", justify="center")
    for name, detail, status in checks:
        color = "green" if status == "OK" else "red"
        table.add_row(name, detail, f"[{color}]{status}[/{color}]")
    console.print(table)

    if any(status != "OK" for _, _, status in checks):
        console.print(f"[red]Something looks off. Please open an issue: {ISSUES_URL}[/red]")
        raise typer.Exit(1)

    console.print(
        f"[dim]All checks passed. Found a bug or dataset issue? {ISSUES_URL}[/dim]"
    )


@app.command("random")
def random_question(
    company: str = typer.Option("", help="Filter by company slug"),
    difficulty: str = typer.Option("", help="Filter by difficulty (easy/medium/hard)"),
    pattern: str = typer.Option("", help="Filter by pattern slug"),
):
    """Pick a random question and open its action screen."""
    index = load_index()
    questions = list(index.questions.values())

    if company:
        questions = index.by_company.get(company, [])
    if difficulty:
        questions = [q for q in questions if q.difficulty == difficulty.lower()]
    if pattern:
        pattern_ids = {q.id for q in index.by_pattern.get(pattern, [])}
        questions = [q for q in questions if q.id in pattern_ids]

    if not questions:
        console.print("[red]No questions match your filters.[/red]")
        raise typer.Exit(1)

    from dooma.commands.practice import _question_actions

    q = random_module.choice(questions)
    _question_actions(q, db.get_all_statuses())


@app.command("bookmarks")
def bookmarks():
    """List bookmarked questions."""
    index = load_index()
    bookmark_ids = db.get_bookmarked_question_ids()
    questions = [index.questions[qid] for qid in bookmark_ids if qid in index.questions]

    if not questions:
        console.print("[dim]No bookmarks yet. Open a question and press 'b' to save it.[/dim]")
        return

    table = display.render_question_table(
        questions,
        title="Bookmarked Questions",
        statuses=db.get_all_statuses(),
        page_size=max(15, len(questions)),
    )
    console.print(table)


@app.command("stats")
def stats():
    """Alias for the progress dashboard."""
    from dooma.commands.dashboard import dashboard as dashboard_cmd

    dashboard_cmd()


@app.command("companies")
def companies(
    limit: int = typer.Option(30, min=1, help="Number of companies to show"),
    json_output: bool = typer.Option(False, "--json", help="Output companies as JSON"),
):
    """List companies with the most available questions."""
    index = load_index()
    company_data = [
        (cid, company.name, len(index.by_company.get(cid, [])))
        for cid, company in index.companies.items()
    ]
    company_data.sort(key=lambda item: item[2], reverse=True)
    company_data = company_data[:limit]
    if json_output:
        typer.echo(
            json.dumps(
                [
                    {"id": cid, "name": name, "question_count": count}
                    for cid, name, count in company_data
                ],
                separators=(",", ":"),
            )
        )
        return
    console.print(display.render_company_list(company_data))


@app.command("search")
def search(
    query: str | None = typer.Argument(None, help="Search query"),
    limit: int = typer.Option(20, min=1, help="Max results"),
    json_output: bool = typer.Option(False, "--json", help="Output results as compact JSON"),
):
    """Fuzzy search across question titles, patterns, and topics."""
    index = load_index()

    if query is None:
        try:
            query = Prompt.ask("[bold]Search[/bold]")
        except (EOFError, typer.Abort):
            raise typer.Exit(0)

    if not query.strip():
        console.print("[dim]Empty query.[/dim]")
        raise typer.Exit(0)

    results = fuzzy_search(query, index, limit=limit)
    if not results:
        if json_output:
            typer.echo(json.dumps([]))
        else:
            console.print(f"[red]No results for '{query}'[/red]")
        raise typer.Exit(0)

    statuses = db.get_all_statuses()

    if json_output:
        payload = [
            {
                "id": q.id,
                "title": q.title,
                "difficulty": q.difficulty,
                "url": q.url,
                "frequency_tier": q.frequency_tier,
                "status": statuses.get(q.id, "unsolved"),
            }
            for q in results
        ]
        typer.echo(json.dumps(payload, separators=(",", ":")))
    else:
        table = display.render_question_table(results, title=f"Search: {query}", statuses=statuses)
        console.print(table)


@app.command("patterns")
def patterns():
    """List DSA patterns and question counts."""
    index = load_index()
    table = Table(title="Patterns", show_header=True, header_style="bold #E74C3C")
    table.add_column("Pattern", style="#F7CA18")
    table.add_column("Slug", style="dim")
    table.add_column("Questions", justify="right")

    for pattern_obj in sorted(index.patterns.values(), key=lambda p: p.name):
        table.add_row(
            pattern_obj.name,
            pattern_obj.id,
            str(len(index.by_pattern.get(pattern_obj.id, []))),
        )
    console.print(table)


@app.command("sheets")
def sheets():
    """List curated sheets."""
    index = load_index()
    table = Table(title="Sheets", show_header=True, header_style="bold #E74C3C")
    table.add_column("Sheet", style="#F7CA18")
    table.add_column("Slug", style="dim")
    table.add_column("Questions", justify="right")
    table.add_column("Description")

    for sheet_obj in sorted(index.sheets.values(), key=lambda s: s.name):
        table.add_row(
            sheet_obj.name,
            sheet_obj.id,
            str(len(index.by_sheet.get(sheet_obj.id, []))),
            sheet_obj.description,
        )
    console.print(table)


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


@app.command("paths")
def paths_cmd():
    """Print local config and state database paths."""
    console.print(f"Config path: {get_config_path()}")
    console.print(f"State database path: {db.get_db_path()}")


@app.callback(invoke_without_command=True)
def main(
    ctx: typer.Context,
    version_flag: bool = typer.Option(
        False,
        "--version",
        "-V",
        callback=_version_callback,
        is_eager=True,
        help="Print version and exit.",
    ),
):
    """Dooma home — interactive DSA prep hub."""
    del version_flag

    if ctx.invoked_subcommand is not None:
        return

    # Onboarding
    if not is_onboarded():
        answers = show_onboarding()
        save_config(answers)

    try:
        index = load_index()
        _first_run = True
        while True:
            from dooma import __version__
            console.clear()

            if _first_run:
                from dooma.display import animate_logo
                animate_logo(version=__version__)
                _first_run = False
            else:
                logo = render_logo(version=__version__)
                console.print(logo)

            console.print()  # Just an empty line spacing

            console.print("\n[bold #E74C3C]Commands:[/bold #E74C3C]")
            menu = [
                ("1", "practice", "Pattern-first question browser"),
                ("2", "browse", "Browse patterns & companies"),
                ("3", "search", "Fuzzy search questions"),
                ("4", "sheet", "Curated roadmaps"),
                ("5", "mock", "Timed mock interview"),
                ("6", "dashboard", "Your progress stats"),
                ("7", "guide", "Commands, workflows, and support"),
                ("8", "quit", "Exit Dooma"),
            ]
            for key, cmd, desc in menu:
                console.print(f"  [bold #F7CA18]{key}[/bold #F7CA18]  {cmd:<12} [dim]{desc}[/dim]")

            choice = Prompt.ask("\nYour choice", default="8")
            choice = choice.strip().lower()
            if choice.startswith("dooma "):
                choice = choice.removeprefix("dooma ").strip()

            if choice in ("q", "0", "8", "quit", "exit"):
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
            elif choice in ("7", "help", "guide", "h", "?"):
                guide()
                Prompt.ask("\nPress Enter to continue")
            elif choice in ("version", "--version", "-v"):
                console.print(f"[bold #F39C12]dooma {__version__}[/bold #F39C12]")
                Prompt.ask("\nPress Enter to continue")
    except (KeyboardInterrupt, EOFError, typer.Abort):
        console.print("\n[bold #F39C12]Goodbye! 🚀[/bold #F39C12]")
        raise typer.Exit(0)


if __name__ == "__main__":
    app()
