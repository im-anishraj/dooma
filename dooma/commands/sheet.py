"""dooma sheet — roadmap/sheet mode."""

from __future__ import annotations

import typer
from rich.prompt import Prompt
from rich.table import Table

from dooma import db, display
from dooma.display import console
from dooma.loader import load_index

app = typer.Typer(help="Work through curated question sheets.")


def run_sheet(sheet_id: str = ""):
    """Core sheet logic — callable from menu or CLI."""
    index = load_index()

    if not sheet_id:
        console.clear()
        table = Table(title="Available Sheets", show_header=True, header_style="bold #E74C3C", expand=True)
        table.add_column("#", justify="right", style="#F39C12", width=4)
        table.add_column("Sheet", style="white", ratio=2)
        table.add_column("Questions", justify="right", style="#F7CA18", width=10)
        table.add_column("Description", style="dim", ratio=3)

        sheet_list = sorted(index.sheets.values(), key=lambda s: s.name)
        for i, s in enumerate(sheet_list, 1):
            count = len(index.by_sheet.get(s.id, []))
            table.add_row(str(i), s.name, str(count), s.description)

        console.print(table)
        choice = Prompt.ask("\nSelect sheet number or q to quit", default="q")
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(sheet_list):
                sheet_id = sheet_list[idx].id
        if not sheet_id:
            return

    questions = index.by_sheet.get(sheet_id, [])
    if not questions:
        console.print(f"[red]Sheet '{sheet_id}' not found or empty.[/red]")
        return

    sheet_obj = index.sheets.get(sheet_id)
    sheet_name = sheet_obj.name if sheet_obj else sheet_id
    statuses = db.get_all_statuses()
    page = 0
    page_size = 15

    while True:
        console.clear()
        table = display.render_question_table(
            questions, title=f"Sheet: {sheet_name}", statuses=statuses, page=page, page_size=page_size,
        )
        console.print(table)

        solved = sum(1 for q in questions if statuses.get(q.id) == "solved")
        console.print(f"\n[bold #F39C12]Progress: {solved}/{len(questions)}[/bold #F39C12]")
        console.print("[dim]n/p: pages • # to select • q: back[/dim]")

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
                from dooma.commands.practice import _question_actions

                _question_actions(questions[idx], statuses)


@app.callback(invoke_without_command=True)
def sheet(
    sheet_id: str = typer.Argument("", help="Sheet slug (e.g. blind-75)"),
):
    """Load a curated question sheet/roadmap."""
    run_sheet(sheet_id=sheet_id)
