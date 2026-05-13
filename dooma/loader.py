"""Loader — reads YAML data files and builds the in-memory Index.

Public API
----------
load_index() → Index
    Returns a cached Index instance.  Safe to call multiple times.
"""

from __future__ import annotations

from pathlib import Path

import yaml  # type: ignore[import-untyped]

from dooma.models import Company, Index, Pattern, Question, Sheet

# Module-level cache — built once per process.
_cached_index: Index | None = None

_PACKAGE_DATA_DIR = Path(__file__).resolve().parent / "data"
_PROJECT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Prefer packaged data for installed wheels, with a source-tree fallback.
_DATA_DIR = _PACKAGE_DATA_DIR if _PACKAGE_DATA_DIR.exists() else _PROJECT_DATA_DIR


def _load_yaml(path: Path) -> dict:
    """Read a single YAML file and return its contents as a dict."""
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def load_index(*, data_dir: Path | None = None, force: bool = False) -> Index:
    """Build (or return cached) in-memory index from data/ YAML files.

    Parameters
    ----------
    data_dir : Path, optional
        Override the default data directory (useful for testing).
    force : bool
        Rebuild the index even if already cached.
    """
    global _cached_index
    if _cached_index is not None and not force and data_dir is None:
        return _cached_index

    base = data_dir or _DATA_DIR
    idx = Index()
    by_company_pairs: dict[str, list[tuple[Question, float]]] = {}

    # --- Patterns -----------------------------------------------------------
    patterns_dir = base / "patterns"
    if patterns_dir.is_dir():
        for fp in sorted(patterns_dir.glob("*.yaml")):
            d = _load_yaml(fp)
            p = Pattern(id=d.get("id", fp.stem), name=d.get("name", ""), description=d.get("description", ""))
            idx.patterns[p.id] = p

    # --- Companies -----------------------------------------------------------
    companies_dir = base / "companies"
    if companies_dir.is_dir():
        for fp in sorted(companies_dir.glob("*.yaml")):
            d = _load_yaml(fp)
            c = Company(id=d.get("id", fp.stem), name=d.get("name", ""), description=d.get("description", ""))
            idx.companies[c.id] = c

    # --- Sheets --------------------------------------------------------------
    sheets_dir = base / "sheets"
    if sheets_dir.is_dir():
        for fp in sorted(sheets_dir.glob("*.yaml")):
            d = _load_yaml(fp)
            s = Sheet(
                id=d.get("id", fp.stem),
                name=d.get("name", ""),
                description=d.get("description", ""),
                questions=d.get("questions", []),
            )
            idx.sheets[s.id] = s

    # --- Questions -----------------------------------------------------------
    questions_dir = base / "questions"
    if questions_dir.is_dir():
        for fp in sorted(questions_dir.glob("*.yaml")):
            d = _load_yaml(fp)
            q = Question(
                id=d.get("id", fp.stem),
                title=d.get("title", ""),
                url=d.get("url", ""),
                difficulty=d.get("difficulty", ""),
                frequency_tier=d.get("frequency_tier", "medium"),
                patterns=d.get("patterns", []),
                topics=d.get("topics", []),
                companies=d.get("companies", {}),
                sheets=d.get("sheets", []),
                prerequisites=d.get("prerequisites", []),
                related=d.get("related", []),
            )
            idx.questions[q.id] = q

            # by_difficulty
            if q.difficulty:
                idx.by_difficulty.setdefault(q.difficulty, []).append(q)

            # by_pattern
            for pat in q.patterns:
                idx.by_pattern.setdefault(pat, []).append(q)

            # by_company — sorted by frequency desc (done after all loaded)
            for comp, meta in q.companies.items():
                by_company_pairs.setdefault(comp, []).append(
                    (q, meta.get("frequency", 0))
                )

            # by_sheet
            for sh in q.sheets:
                idx.by_sheet.setdefault(sh, []).append(q)

    # Also populate by_company from the companies map in each question
    # Sort by_company lists by frequency descending
    for comp, pairs in by_company_pairs.items():
        pairs.sort(key=lambda pair: pair[1], reverse=True)
        idx.by_company[comp] = [q for q, _ in pairs]

    # Populate by_sheet from Sheet objects for sheets that have question lists
    for sheet_id, sheet_obj in idx.sheets.items():
        if sheet_id not in idx.by_sheet and sheet_obj.questions:
            idx.by_sheet[sheet_id] = [
                idx.questions[qid] for qid in sheet_obj.questions if qid in idx.questions
            ]
        elif sheet_id not in idx.by_sheet:
            idx.by_sheet[sheet_id] = []

    # Cache result
    if data_dir is None:
        _cached_index = idx

    return idx
