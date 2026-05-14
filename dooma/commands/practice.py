"""dooma practice — pattern-first question browser."""

from __future__ import annotations

import webbrowser

import typer
from rich.prompt import Prompt

from dooma import db, display
from dooma.display import console
from dooma.loader import load_index

app = typer.Typer(help="Practice questions by pattern, company, or difficulty.")


def run_practice(company: str = "", difficulty: str = "", pattern: str = ""):
    """Core practice logic — callable from menu or CLI."""
    index = load_index()
    questions = list(index.questions.values())

    if company:
        questions = index.by_company.get(company, [])
        if not questions:
            console.print(f"[red]No questions found for company '{company}'[/red]")
            return
    if difficulty:
        questions = [q for q in questions if q.difficulty == difficulty.lower()]
    if pattern:
        pat_qs = set(q.id for q in index.by_pattern.get(pattern, []))
        questions = [q for q in questions if q.id in pat_qs]

    if not questions:
        console.print("[red]No questions match your filters.[/red]")
        return

    statuses = db.get_all_statuses()
    page = 0
    page_size = 15

    while True:
        console.clear()
        title = "Practice Mode"
        if company:
            title += f" — {company}"
        if difficulty:
            title += f" [{difficulty}]"
        if pattern:
            title += f" ({pattern})"

        table = display.render_question_table(
            questions, title=title, statuses=statuses, page=page, page_size=page_size,
        )
        console.print(table)
        console.print("\n[dim]n/p: navigate pages • # to select • o: open URL • m: cycle status • b: bookmark • /: search • q: quit[/dim]")

        choice = Prompt.ask("\nAction", default="")
        choice = choice.strip()

        if choice in ("q", "Q") or choice == "\x1b":
            return
        elif choice == "n" and (page + 1) * page_size < len(questions):
            page += 1
        elif choice == "p" and page > 0:
            page -= 1
        elif choice == "/":
            _inline_search(index, statuses)
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(questions):
                _question_actions(questions[idx], statuses)


@app.callback(invoke_without_command=True)
def practice(
    company: str = typer.Option("", help="Filter by company slug"),
    difficulty: str = typer.Option("", help="Filter by difficulty (easy/medium/hard)"),
    pattern: str = typer.Option("", help="Filter by pattern slug"),
):
    """Interactive practice session with optional filters."""
    run_practice(company=company, difficulty=difficulty, pattern=pattern)


def _question_actions(q, statuses):
    """Show a question detail and handle actions."""
    while True:
        console.clear()
        st = db.get_status(q.id)
        bm = "📌" if db.is_bookmarked(q.id) else ""
        dc = display.difficulty_color(q.difficulty)
        console.print(f"\n[bold]{q.title}[/bold] {bm}")
        console.print(f"  ID: {q.id}  Difficulty: [{dc}]{q.difficulty}[/{dc}]  Status: {display.status_icon(st)} {st}")
        console.print(f"  URL: [blue]{q.url}[/blue]")
        note = db.get_note(q.id)
        if note:
            console.print(f"  Note: {note}")
        console.print("\n[dim]o: open URL • m: cycle status • b: bookmark • n: edit note • q: back[/dim]")

        action = Prompt.ask("Action", default="q")
        if action == "o" and q.url:
            webbrowser.open(q.url)
        elif action == "m":
            cycle = ["unsolved", "attempted", "solved", "skipped"]
            cur = cycle.index(st) if st in cycle else 0
            new_st = cycle[(cur + 1) % len(cycle)]
            db.set_status(q.id, new_st)
            statuses[q.id] = new_st
            if new_st == "solved":
                db.increment_streak_today()
            console.print(f"[green]Status → {new_st}[/green]")
        elif action == "b":
            result = db.toggle_bookmark(q.id)
            console.print(f"[green]{'Bookmarked' if result else 'Unbookmarked'}[/green]")
        elif action == "n":
            existing = db.get_note(q.id) or ""
            new_note = Prompt.ask("Note", default=existing)
            if new_note:
                db.set_note(q.id, new_note)
        elif action in ("q", "Q"):
            return


def _inline_search(index, statuses):
    """Quick inline search from practice mode."""
    from dooma.search import fuzzy_search
    query = Prompt.ask("[bold]Search[/bold]", default="")
    if not query:
        return
    results = fuzzy_search(query, index)
    if not results:
        console.print("[red]No results.[/red]")
        Prompt.ask("Press Enter")
        return
    table = display.render_question_table(results, title=f"Search: {query}", statuses=statuses)
    console.print(table)
    Prompt.ask("Press Enter to return")
