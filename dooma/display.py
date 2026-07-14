"""Rich rendering helpers — tables, panels, prompts for the TUI."""

from __future__ import annotations

import sys

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from dooma.models import Question


def _prefer_utf8_streams() -> None:
    """Avoid UnicodeEncodeError on Windows consoles using legacy code pages."""
    for stream in (sys.stdout, sys.stderr):
        encoding = getattr(stream, "encoding", None) or ""
        reconfigure = getattr(stream, "reconfigure", None)
        if reconfigure is not None and "utf" not in encoding.lower():
            try:
                reconfigure(encoding="utf-8", errors="replace")
            except (OSError, ValueError):
                pass


_prefer_utf8_streams()

console = Console()

_IMAGE_LOGO_WIDTH = 55  # For compact fallback logic

def _render_compact_logo() -> Text:
    """Return a fallback compact text wordmark."""
    return Text.from_markup(
        "[#F39C12]DOOMA[/] - [#F7CA18]technical interview prep[/]\n"
        "[dim]17,931 interview mappings • offline first[/]"
    )


def render_logo(version: str | None = None, eyes: str = "o,o") -> Text:
    """Return the redesigned Dooma terminal wordmark."""
    if console.color_system is None or console.size.width < _IMAGE_LOGO_WIDTH:
        return _render_compact_logo()

    # Simple, cute Owl icon (Wisdom/Learning) aligned left
    logo_raw = [
        " ___   ",
        f"({eyes})  ",
        "{`\"'}  ",
        "-\"-\"-  "
    ]
    
    text = Text()
    # Line 1
    text.append(logo_raw[0] + "\n", style="bold #F39C12")
    
    # Line 2 (Tags)
    text.append(logo_raw[1], style="bold #F39C12")
    text.append("technical interview prep", style="#F7CA18")
    text.append(" • ", style="dim")
    text.append("17,931 interview mappings", style="#E74C3C")
    text.append(" • ", style="dim")
    text.append("offline first\n", style="#F39C12")
    
    # Line 3 (Version)
    text.append(logo_raw[2], style="bold #F39C12")
    if version:
        text.append(f"Dooma v{version}\n", style="bold #F39C12")
    else:
        text.append("\n")
        
    # Line 4
    text.append(logo_raw[3] + "\n", style="bold #F39C12")

    return text


def animate_logo(version: str | None = None) -> None:
    """Animate the owl logo on startup."""
    import time

    from rich.live import Live

    if console.color_system is None or console.size.width < _IMAGE_LOGO_WIDTH:
        console.print(_render_compact_logo())
        return

    frames = [
        ("-,-", 0.3),
        ("D  ", 0.15),
        ("DS ", 0.15),
        ("DSA", 0.6),
        ("-,-", 0.1),
        ("o,o", 0.1),
        ("O,O", 0.6),
    ]

    # Use transient=False so it leaves the final frame on the screen
    with Live(render_logo(version, frames[0][0]), console=console, transient=False, refresh_per_second=20) as live:
        for eyes, duration in frames:
            live.update(render_logo(version, eyes))
            time.sleep(duration)

def show_onboarding() -> dict:
    """Run the first-time onboarding flow and return config answers."""
    from rich.prompt import Prompt

    console.clear()
    console.print(Panel("[bold #F39C12]Welcome to Dooma![/bold #F39C12]\nLet's set up your profile.", border_style="#F39C12"))

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


def difficulty_color(diff: str) -> str:
    """Return a Rich color string for a difficulty level."""
    return {"easy": "green", "medium": "#F7CA18", "hard": "#E74C3C"}.get(diff, "white")


def status_icon(status: str) -> str:
    """Return an emoji for a question status."""
    return {
        "solved": "[bold green]✔[/bold green]",
        "attempted": "[bold #F39C12]▶[/bold #F39C12]",
        "skipped": "[bold dim]⏭[/bold dim]"
    }.get(status, "[dim]·[/dim]")


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

def render_stats_dashboard(stats: dict) -> Panel:
    """Render the dashboard stats panel."""
    text = Text.from_markup(
        "[bold #F39C12]📊 Your Progress Dashboard[/bold #F39C12]\n"
        f"  [bold green]○[/bold green] Solved:     [green]{stats.get('solved', 0)}[/green]\n"
        f"  [bold #F39C12]◇[/bold #F39C12] Attempted:  [yellow]{stats.get('attempted', 0)}[/yellow]\n"
        f"  [bold dim]×[/bold dim]  Skipped:    [dim]{stats.get('skipped', 0)}[/dim]\n"
        f"  📌 Bookmarks:  {stats.get('bookmarks', 0)}\n"
        f"  📝 Notes:      {stats.get('notes', 0)}\n"
        f"  🔥 Streak:     {stats.get('streak_days', 0)} day(s)  ({stats.get('streak_today', 0)} today)\n"
    )
    return Panel(text, border_style="#F39C12")
