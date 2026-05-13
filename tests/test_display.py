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

    assert len(logo.plain.splitlines()) == 15
    assert max(map(len, logo.plain.splitlines())) == 76


def test_render_logo_uses_compact_logo_on_narrow_terminal(monkeypatch):
    monkeypatch.setattr(
        display,
        "console",
        Console(force_terminal=True, color_system="truecolor", width=60),
    )

    logo = display.render_logo()

    assert len(logo.plain.splitlines()) == 7
    assert "terminal DSA forge" in logo.plain
