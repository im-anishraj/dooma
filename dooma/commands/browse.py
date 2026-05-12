"""dooma browse — browse patterns and companies."""

from __future__ import annotations

import webbrowser

import typer
from rich.prompt import Prompt

from dooma import db, display
from dooma.loader import load_index
from dooma.display import console

app = typer.Typer(help="Browse patterns or companies.")


@app.callback(invoke_without_command=True)
def browse(
    ctx: typer.Context,
    target: str = typer.Argument("patterns", help="What to browse: patterns | companies"),
):
    """Browse the pattern library or company list."""
    if ctx.invoked_subcommand is not None:
        return
    if target == "companies":
        _browse_companies()
    else:
        _browse_patterns()


def _browse_patterns():
    index = load_index()
    patterns = sorted(index.patterns.values(), key=lambda p: p.name)

    console.clear()
    from rich.table import Table
    table = Table(title="Pattern Library", show_header=True, header_style="bold #E74C3C", expand=True)
    table.add_column("#", justify="right", style="#F39C12", width=4)
    table.add_column("Pattern", style="white", ratio=2)
    table.add_column("Questions", justify="right", style="#F7CA18", width=10)
    table.add_column("Description", style="dim", ratio=3)

    for i, p in enumerate(patterns, 1):
        count = len(index.by_pattern.get(p.id, []))
        table.add_row(str(i), p.name, str(count), p.description)

    console.print(table)
    console.print("\n[dim]Enter a number to view questions for that pattern, or q to quit[/dim]")

    while True:
        choice = Prompt.ask("Select", default="q")
        if choice in ("q", "Q"):
            return
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(patterns):
                pat = patterns[idx]
                qs = index.by_pattern.get(pat.id, [])
                if qs:
                    statuses = db.get_all_statuses()
                    table = display.render_question_table(qs, title=f"Pattern: {pat.name}", statuses=statuses)
                    console.print(table)
                else:
                    console.print("[dim]No questions tagged with this pattern yet.[/dim]")


def _browse_companies():
    index = load_index()
    # Build list of (id, display_name, count) sorted by count desc
    company_data = []
    for cid, company in sorted(index.companies.items(), key=lambda x: x[1].name):
        count = len(index.by_company.get(cid, []))
        company_data.append((cid, company.name, count))

    # Sort by question count descending
    company_data.sort(key=lambda x: x[2], reverse=True)

    page = 0
    page_size = 30

    while True:
        console.clear()
        total = len(company_data)
        start = page * page_size
        end = min(start + page_size, total)
        page_items = company_data[start:end]

        table = display.render_company_list(page_items)
        console.print(table)
        console.print(f"\n[dim]Page {page+1}/{(total + page_size - 1)//page_size} • n/p: navigate • # to select • q: quit[/dim]")

        choice = Prompt.ask("Select", default="q")
        if choice in ("q", "Q"):
            return
        elif choice == "n" and end < total:
            page += 1
        elif choice == "p" and page > 0:
            page -= 1
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(page_items):
                cid = page_items[idx][0]
                qs = index.by_company.get(cid, [])
                _show_company_questions(page_items[idx][1], qs)


def _show_company_questions(name: str, questions):
    """Show questions for a selected company."""
    statuses = db.get_all_statuses()
    page = 0
    page_size = 15

    while True:
        console.clear()
        table = display.render_question_table(
            questions, title=f"Company: {name}", statuses=statuses, page=page, page_size=page_size,
        )
        console.print(table)
        console.print(f"\n[dim]n/p: pages • # to select • o: open URL • m: status • b: bookmark • q: back[/dim]")

        choice = Prompt.ask("Action", default="q")
        if choice in ("q", "Q"):
            return
        elif choice == "n" and (page + 1) * page_size < len(questions):
            page += 1
        elif choice == "p" and page > 0:
            page -= 1
        elif choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(questions):
                q = questions[idx]
                webbrowser.open(q.url)
