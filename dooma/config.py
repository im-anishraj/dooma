"""Configuration — reads/writes ~/.dooma/config.json."""

from __future__ import annotations

import json
from pathlib import Path

_CONFIG_PATH = Path.home() / ".dooma" / "config.json"

_DEFAULTS = {
    "goal": "",
    "level": "",
    "roadmap": "",
    "onboarding_done": False,
}


def load_config(config_path: Path | None = None) -> dict:
    """Load config from disk, falling back to defaults."""
    path = config_path or _CONFIG_PATH
    if path.exists():
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return {**_DEFAULTS, **data}
    return dict(_DEFAULTS)


def save_config(config: dict, config_path: Path | None = None) -> None:
    """Persist config to disk."""
    path = config_path or _CONFIG_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(config, f, indent=2)


def is_onboarded(config_path: Path | None = None) -> bool:
    """Check whether the onboarding flow has been completed."""
    return load_config(config_path).get("onboarding_done", False)


def reset_config(config_path: Path | None = None) -> None:
    """Reset config to defaults."""
    save_config(dict(_DEFAULTS), config_path)
