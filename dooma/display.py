"""Rich rendering helpers — tables, panels, prompts for the TUI."""

from __future__ import annotations

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from dooma.models import Question

console = Console()


def difficulty_color(diff: str) -> str:
    """Return a Rich color string for a difficulty level."""
    return {"easy": "green", "medium": "#F7CA18", "hard": "#E74C3C"}.get(diff, "white")


def status_icon(status: str) -> str:
    """Return an emoji for a question status."""
    return {"solved": "✅", "attempted": "🔄", "skipped": "⏭️"}.get(status, "⬜")


def render_question_table(
    questions: list[Question],
    *,
    title: str = "Questions",
    statuses: dict[str, str] | None = None,
    page: int = 0,
    page_size: int = 15,
) -> Table:
    """Build a Rich Table for a list of questions with pagination."""
    total = len(questions)
    start = page * page_size
    end = min(start + page_size, total)
    page_qs = questions[start:end]

    table = Table(
        title=f"{title}  (showing {start+1}–{end} of {total})",
        show_header=True,
        header_style="bold #E74C3C",
        expand=True,
    )
    table.add_column("#", justify="right", style="#F39C12", no_wrap=True, width=4)
    table.add_column("Status", width=4)
    table.add_column("Title", style="white", ratio=3)
    table.add_column("Difficulty", width=10)
    table.add_column("Freq", style="#F7CA18", width=6)
    table.add_column("URL", style="blue", ratio=2)

    sts = statuses or {}
    for i, q in enumerate(page_qs, start=start + 1):
        dc = difficulty_color(q.difficulty)
        diff_fmt = f"[{dc}]{q.difficulty or 'N/A'}[/{dc}]"
        icon = status_icon(sts.get(q.id, "unsolved"))
        table.add_row(str(i), icon, q.title, diff_fmt, q.frequency_tier, q.url)

    return table


def render_company_list(companies: list[tuple[str, str, int]]) -> Table:
    """Render a table of companies with question counts.

    Each item is (company_id, display_name, question_count).
    """
    table = Table(title="Companies", show_header=True, header_style="bold #E74C3C", expand=True)
    table.add_column("#", justify="right", style="#F39C12", width=4)
    table.add_column("Company", style="white", ratio=2)
    table.add_column("Questions", justify="right", style="#F7CA18", width=10)

    for i, (cid, name, count) in enumerate(companies, 1):
        table.add_row(str(i), name, str(count))
    return table


def render_dashboard(stats: dict) -> Panel:
    """Render the dashboard stats panel."""
    lines = [
        f"[bold #F39C12]📊 Your Progress Dashboard[/bold #F39C12]\n",
        f"  ✅ Solved:     [green]{stats.get('solved', 0)}[/green]",
        f"  🔄 Attempted:  [yellow]{stats.get('attempted', 0)}[/yellow]",
        f"  ⏭️  Skipped:    [dim]{stats.get('skipped', 0)}[/dim]",
        f"  📌 Bookmarks:  {stats.get('bookmarks', 0)}",
        f"  📝 Notes:      {stats.get('notes', 0)}",
        f"  🔥 Streak:     {stats.get('streak_days', 0)} day(s)  ({stats.get('streak_today', 0)} today)",
    ]
    return Panel("\n".join(lines), border_style="#F39C12")


def render_logo() -> Text:
    """Return the Dooma ASCII logo."""
    return Text.from_markup(
        "[#F39C12]██████████████[/]\n"
        "[#F39C12]██[/][#E74C3C]████████████[/][#F7CA18]▄▄[/]\n"
        "[#F39C12]██[/][#E74C3C]██[/]        [#F7CA18]██[/]\n"
        "[#F39C12]██[/][#E74C3C]██[/]        [#F7CA18]██[/]\n"
        "[#F39C12]██[/][#E74C3C]██[/]        [#F7CA18]██[/]\n"
        "[#F39C12]██[/][#E74C3C]██[/]        [#F7CA18]██[/]\n"
        "[#F39C12]██[/][#E74C3C]████████████[/][#F7CA18]▀▀[/]\n"
        "[#F39C12]██████████████[/]"
    )


def show_onboarding() -> dict:
    """Run the first-time onboarding flow and return config answers."""
    from rich.prompt import Prompt

    console.clear()
    console.print(Panel("[bold #F39C12]Welcome to Dooma 2.0![/bold #F39C12]\nLet's set up your profile.", border_style="#F39C12"))

    goal = Prompt.ask(
        "\n[bold]What's your main goal?[/bold]",
        choices=["interview_prep", "learning", "both"],
        default="both",
    )
    level = Prompt.ask(
        "[bold]Your current experience level?[/bold]",
        choices=["beginner", "intermediate", "experienced"],
        default="beginner",
    )
    roadmap = Prompt.ask(
        "[bold]Pick a starting roadmap[/bold]",
        choices=["blind-75", "neetcode-150", "striver-sde", "skip"],
        default="blind-75",
    )

    return {"goal": goal, "level": level, "roadmap": roadmap, "onboarding_done": True}
