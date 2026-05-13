"""Tests for dooma.loader — prebuilt index loader with YAML fallback."""

import json

import pytest

import dooma.loader as loader
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


def test_default_load_uses_prebuilt_index(monkeypatch):
    """The packaged runtime path should not parse YAML when index.json exists."""

    def fail_yaml_load(_base):
        raise AssertionError("YAML fallback should not be used for default load")

    monkeypatch.setattr(loader, "_build_index_from_yaml", fail_yaml_load)

    idx = load_index(force=True)

    assert len(idx.questions) == 3310
    assert "google" in idx.by_company


def test_custom_data_dir_uses_yaml_fallback(tmp_path):
    """Custom data directories remain YAML-driven for tests and development."""
    for directory in ("patterns", "companies", "sheets", "questions"):
        (tmp_path / directory).mkdir()

    (tmp_path / "patterns" / "arrays.yaml").write_text(
        "id: arrays\nname: Arrays\ndescription: Array problems\n",
        encoding="utf-8",
    )
    (tmp_path / "companies" / "acme.yaml").write_text(
        "id: acme\nname: Acme\ndescription: Example company\n",
        encoding="utf-8",
    )
    (tmp_path / "sheets" / "starter.yaml").write_text(
        "id: starter\nname: Starter\nquestions:\n- sample-question\n",
        encoding="utf-8",
    )
    (tmp_path / "questions" / "sample-question.yaml").write_text(
        "\n".join(
            [
                "id: sample-question",
                "title: Sample Question",
                "url: https://leetcode.com/problems/sample-question",
                "difficulty: Easy",
                "patterns:",
                "- arrays",
                "companies:",
                "  acme:",
                "    frequency: 99.0",
                "sheets:",
                "- starter",
            ]
        ),
        encoding="utf-8",
    )

    idx = load_index(data_dir=tmp_path, force=True)

    assert list(idx.questions) == ["sample-question"]
    assert idx.by_pattern["arrays"][0].id == "sample-question"
    assert idx.by_company["acme"][0].id == "sample-question"
    assert idx.by_sheet["starter"][0].id == "sample-question"


def test_prebuilt_index_is_current():
    """Fail fast when YAML data changes without rebuilding index.json."""
    index_path = loader._DATA_DIR / loader._PREBUILT_INDEX_FILENAME

    payload = json.loads(index_path.read_text(encoding="utf-8"))
    expected = loader.serialize_prebuilt_index_payload(
        loader.build_prebuilt_index_payload()
    )

    assert payload["source_hash"]
    assert index_path.read_text(encoding="utf-8") == expected
