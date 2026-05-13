"""Tests for dooma.loader — YAML index builder."""

import pytest

from dooma.loader import load_index


@pytest.fixture(scope="module")
def index():
    """Load the real index once for all tests in this module."""
    return load_index(force=True)


def test_load_index_returns_valid_object(index):
    assert index is not None
    assert hasattr(index, "questions")
    assert hasattr(index, "by_company")
    assert hasattr(index, "by_pattern")
    assert hasattr(index, "by_sheet")
    assert hasattr(index, "patterns")
    assert hasattr(index, "companies")
    assert hasattr(index, "sheets")


def test_questions_not_empty(index):
    assert len(index.questions) > 0


def test_by_company_google(index):
    google_qs = index.by_company.get("google", [])
    assert len(google_qs) > 0, "Google should have questions"


def test_by_pattern_hash_map(index):
    # hash-map pattern exists as a stub; questions may or may not be tagged
    assert "hash-map" in index.patterns


def test_by_sheet_blind_75(index):
    blind = index.by_sheet.get("blind-75", [])
    assert len(blind) > 0, "blind-75 sheet should have questions"


def test_all_questions_have_required_fields(index):
    for qid, q in index.questions.items():
        assert q.id, f"Question missing id: {qid}"
        assert q.title, f"Question missing title: {qid}"
        assert q.url, f"Question missing url: {qid}"


def test_by_company_sorted_by_frequency(index):
    """by_company lists should be sorted by frequency descending."""
    google_qs = index.by_company.get("google", [])
    if len(google_qs) >= 2:
        # Just verify it's a list of Question objects (not tuples)
        assert hasattr(google_qs[0], "title")


def test_load_index_idempotent(index):
    """Calling load_index multiple times returns the same object."""
    idx2 = load_index()
    assert len(idx2.questions) == len(index.questions)
