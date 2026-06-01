"""Loader — reads prebuilt or YAML data files and builds the in-memory Index.

Public API
----------
load_index() → Index
    Returns a cached Index instance. Safe to call multiple times.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from dooma.models import Company, Index, Pattern, Question, Sheet

# Module-level cache — built once per process.
_cached_index: Index | None = None

_PACKAGE_DATA_DIR = Path(__file__).resolve().parent / "data"
_PROJECT_DATA_DIR = Path(__file__).resolve().parent.parent / "data"

# Prefer packaged data for installed wheels, with a source-tree fallback.
_DATA_DIR = _PACKAGE_DATA_DIR if _PACKAGE_DATA_DIR.exists() else _PROJECT_DATA_DIR
_PREBUILT_INDEX_FILENAME = "index.json"
_PREBUILT_SCHEMA_VERSION = 1


def _load_yaml(path: Path) -> dict:
    """Read a single YAML file and return its contents as a dict."""
    with open(path, "r", encoding="utf-8") as fh:
        return yaml.safe_load(fh) or {}


def _iter_yaml_files(base: Path):
    for directory in ("patterns", "companies", "sheets", "questions"):
        data_path = base / directory
        if data_path.is_dir():
            yield from sorted(data_path.glob("*.yaml"))


def _compute_source_hash(base: Path) -> str:
    """Return a deterministic hash for all YAML source files."""
    digest = hashlib.sha256()
    for fp in _iter_yaml_files(base):
        relative = fp.relative_to(base).as_posix()
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        content = fp.read_text(encoding="utf-8")
        digest.update(content.replace("\r\n", "\n").replace("\r", "\n").encode("utf-8"))
        digest.update(b"\0")
    return digest.hexdigest()


def _build_index_from_yaml(base: Path) -> Index:
    """Build an in-memory Index from the canonical YAML dataset."""
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

    return idx


def _question_to_record(question: Question) -> dict[str, Any]:
    return {
        "id": question.id,
        "title": question.title,
        "url": question.url,
        "difficulty": question.difficulty,
        "frequency_tier": question.frequency_tier,
        "patterns": question.patterns,
        "topics": question.topics,
        "companies": question.companies,
        "sheets": question.sheets,
        "prerequisites": question.prerequisites,
        "related": question.related,
    }


def _index_to_prebuilt_payload(index: Index, base: Path) -> dict[str, Any]:
    def question_ids(questions: list[Question]) -> list[str]:
        return [question.id for question in questions]

    return {
        "schema_version": _PREBUILT_SCHEMA_VERSION,
        "source_hash": _compute_source_hash(base),
        "counts": {
            "questions": len(index.questions),
            "company_question_mappings": sum(len(q.companies) for q in index.questions.values()),
            "companies": len(index.companies),
            "patterns": len(index.patterns),
            "sheets": len(index.sheets),
        },
        "questions": {
            qid: _question_to_record(question)
            for qid, question in index.questions.items()
        },
        "patterns": {
            pid: {
                "id": pattern.id,
                "name": pattern.name,
                "description": pattern.description,
            }
            for pid, pattern in index.patterns.items()
        },
        "companies": {
            cid: {
                "id": company.id,
                "name": company.name,
                "description": company.description,
            }
            for cid, company in index.companies.items()
        },
        "sheets": {
            sid: {
                "id": sheet.id,
                "name": sheet.name,
                "description": sheet.description,
                "questions": sheet.questions,
            }
            for sid, sheet in index.sheets.items()
        },
        "by_difficulty": {
            difficulty: question_ids(questions)
            for difficulty, questions in index.by_difficulty.items()
        },
        "by_pattern": {
            pattern: question_ids(questions)
            for pattern, questions in index.by_pattern.items()
        },
        "by_company": {
            company: question_ids(questions)
            for company, questions in index.by_company.items()
        },
        "by_sheet": {
            sheet: question_ids(questions)
            for sheet, questions in index.by_sheet.items()
        },
    }


def build_prebuilt_index_payload(*, data_dir: Path | None = None) -> dict[str, Any]:
    """Build the deterministic JSON payload used by the runtime fast path."""
    base = data_dir or _DATA_DIR
    index = _build_index_from_yaml(base)
    return _index_to_prebuilt_payload(index, base)


def serialize_prebuilt_index_payload(payload: dict[str, Any]) -> str:
    """Serialize a prebuilt index payload deterministically and compactly."""
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ) + "\n"


def _question_refs(question_ids: list[str], questions: dict[str, Question]) -> list[Question]:
    return [questions[qid] for qid in question_ids if qid in questions]


def _index_from_prebuilt_payload(payload: dict[str, Any]) -> Index:
    if payload.get("schema_version") != _PREBUILT_SCHEMA_VERSION:
        raise ValueError("Unsupported prebuilt index schema version")

    idx = Index()
    idx.questions = {
        qid: Question(
            id=record.get("id", qid),
            title=record.get("title", ""),
            url=record.get("url", ""),
            difficulty=record.get("difficulty", ""),
            frequency_tier=record.get("frequency_tier", "medium"),
            patterns=record.get("patterns", []),
            topics=record.get("topics", []),
            companies=record.get("companies", {}),
            sheets=record.get("sheets", []),
            prerequisites=record.get("prerequisites", []),
            related=record.get("related", []),
        )
        for qid, record in payload.get("questions", {}).items()
    }
    idx.patterns = {
        pid: Pattern(
            id=record.get("id", pid),
            name=record.get("name", ""),
            description=record.get("description", ""),
        )
        for pid, record in payload.get("patterns", {}).items()
    }
    idx.companies = {
        cid: Company(
            id=record.get("id", cid),
            name=record.get("name", ""),
            description=record.get("description", ""),
        )
        for cid, record in payload.get("companies", {}).items()
    }
    idx.sheets = {
        sid: Sheet(
            id=record.get("id", sid),
            name=record.get("name", ""),
            description=record.get("description", ""),
            questions=record.get("questions", []),
        )
        for sid, record in payload.get("sheets", {}).items()
    }
    idx.by_difficulty = {
        difficulty: _question_refs(question_ids, idx.questions)
        for difficulty, question_ids in payload.get("by_difficulty", {}).items()
    }
    idx.by_pattern = {
        pattern: _question_refs(question_ids, idx.questions)
        for pattern, question_ids in payload.get("by_pattern", {}).items()
    }
    idx.by_company = {
        company: _question_refs(question_ids, idx.questions)
        for company, question_ids in payload.get("by_company", {}).items()
    }
    idx.by_sheet = {
        sheet: _question_refs(question_ids, idx.questions)
        for sheet, question_ids in payload.get("by_sheet", {}).items()
    }
    return idx


def _load_index_from_prebuilt(path: Path) -> Index:
    with open(path, "r", encoding="utf-8") as fh:
        payload = json.load(fh)
    return _index_from_prebuilt_payload(payload)


def _validate_sheet_references(index: Index) -> None:
    known_sheets = set(index.sheets.keys())
    errors: list[tuple[str, str]] = []
    for question_id, question in index.questions.items():
        for sheet_id in question.sheets:
            if sheet_id not in known_sheets:
                errors.append((question_id, sheet_id))

    if not errors:
        return

    errors.sort()
    details = "\n".join(
        f"- question={question_id} sheet={sheet_id}" for question_id, sheet_id in errors
    )
    raise ValueError(
        "Unknown sheet reference(s) found in question data.\n"
        "Each sheet listed under a question must exist in dooma/data/sheets.\n"
        f"{details}"
    )


def load_index(*, data_dir: Path | None = None, force: bool = False) -> Index:
    """Build (or return cached) in-memory index from a prebuilt or YAML dataset.

    Parameters
    ----------
    data_dir : Path, optional
        Override the default data directory (useful for testing). Custom data
        directories always load from YAML, not from the packaged prebuilt index.
    force : bool
        Rebuild the index even if already cached.
    """
    global _cached_index
    if _cached_index is not None and not force and data_dir is None:
        return _cached_index

    base = data_dir or _DATA_DIR
    prebuilt_path = base / _PREBUILT_INDEX_FILENAME

    if data_dir is None and prebuilt_path.is_file():
        try:
            idx = _load_index_from_prebuilt(prebuilt_path)
        except (OSError, ValueError, TypeError, KeyError, json.JSONDecodeError):
            idx = _build_index_from_yaml(base)
    else:
        idx = _build_index_from_yaml(base)

    _validate_sheet_references(idx)

    # Cache result
    if data_dir is None:
        _cached_index = idx

    return idx
