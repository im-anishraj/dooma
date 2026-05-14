"""Dooma data models — dataclasses for Question, Pattern, Company, Sheet."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class Question:
    """A single LeetCode-style question."""

    id: str
    title: str
    url: str = ""
    difficulty: str = ""  # easy | medium | hard | ""
    frequency_tier: str = "medium"  # high | medium | low | rare

    patterns: list[str] = field(default_factory=list)
    topics: list[str] = field(default_factory=list)
    companies: dict[str, dict] = field(default_factory=dict)
    sheets: list[str] = field(default_factory=list)
    prerequisites: list[str] = field(default_factory=list)
    related: list[str] = field(default_factory=list)


@dataclass
class Pattern:
    """A DSA pattern (e.g. sliding-window, two-pointers)."""

    id: str
    name: str
    description: str = ""


@dataclass
class Company:
    """A company entry."""

    id: str
    name: str
    description: str = ""


@dataclass
class Sheet:
    """A curated question roadmap."""

    id: str
    name: str
    description: str = ""
    questions: list[str] = field(default_factory=list)


@dataclass
class Index:
    """The in-memory index built from all YAML data files."""

    questions: dict[str, Question] = field(default_factory=dict)
    by_pattern: dict[str, list[Question]] = field(default_factory=dict)
    by_company: dict[str, list[Question]] = field(default_factory=dict)
    by_difficulty: dict[str, list[Question]] = field(default_factory=dict)
    by_sheet: dict[str, list[Question]] = field(default_factory=dict)
    patterns: dict[str, Pattern] = field(default_factory=dict)
    companies: dict[str, Company] = field(default_factory=dict)
    sheets: dict[str, Sheet] = field(default_factory=dict)
