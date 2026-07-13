"""Tests for terminal rendering helpers."""

from rich.console import Console

import dooma.display as display


def test_render_logo_uses_image_logo_on_wide_color_terminal(monkeypatch):
    monkeypatch.setattr(
        display,
        "console",
        Console(force_terminal=True, color_system="truecolor", width=120),
    )

    logo = display.render_logo()

    # The new horizontally aligned Owl logo is 4 lines long
    assert len(logo.plain.splitlines()) == 4
    assert "terminal DSA forge" in logo.plain


def test_render_logo_uses_compact_logo_on_narrow_terminal(monkeypatch):
    monkeypatch.setattr(
        display,
        "console",
        Console(force_terminal=True, color_system="truecolor", width=40),
    )

    logo = display.render_logo()

    # The new compact logo is 2 lines long
    assert len(logo.plain.splitlines()) == 2
    assert "terminal DSA forge" in logo.plain
