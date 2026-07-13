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
        "[#F39C12]DOOMA[/] - [#F7CA18]terminal DSA forge[/]\n"
        "[dim]17,931 interview mappings • offline first[/]"
    )


def render_logo(version: str = None) -> Text:
    """Return the redesigned Dooma terminal wordmark."""
    if console.color_system is None or console.size.width < _IMAGE_LOGO_WIDTH:
        return _render_compact_logo()

    # Simple, cute Owl icon (Wisdom/Learning) aligned left
    logo_raw = [
        "   ___     ",
        "  (o,o)    ",
        "  {`\"'}    ",
        "  -\"-\"-    "
    ]
    
    text = Text()
    # Line 1
    text.append(logo_raw[0] + "\n", style="bold #F39C12")
    
    # Line 2 (Tags)
    text.append(logo_raw[1], style="bold #F39C12")
    text.append("terminal DSA forge", style="#F7CA18")
    text.append(" • ", style="dim")
    text.append("17,931 interview mappings", style="#E74C3C")
    text.append(" • ", style="dim")
    text.append("offline first\n", style="#F39C12")
    
    # Line 3 (Version)
    text.append(logo_raw[2], style="bold #F39C12")
    if version:
        text.append(f"Dooma v{version} — DSA Interview Prep\n", style="bold #F39C12")
    else:
        text.append("\n")
        
    # Line 4
    text.append(logo_raw[3] + "\n", style="bold #F39C12")

    return text

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
