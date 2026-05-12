"""Tests for dooma.search — fuzzy search."""

import pytest
from dooma.loader import load_index
from dooma.search import fuzzy_search


@pytest.fixture(scope="module")
def index():
    return load_index(force=True)


def test_search_two_sum(index):
    results = fuzzy_search("two sum", index)
    assert len(results) > 0
    assert results[0].id == "two-sum"


def test_search_sliding(index):
    results = fuzzy_search("sliding", index)
    assert len(results) > 0
    # At least one result should have "sliding" in its title
    titles = [r.title.lower() for r in results]
    assert any("sliding" in t for t in titles)


def test_empty_query(index):
    results = fuzzy_search("", index)
    assert results == []


def test_whitespace_query(index):
    results = fuzzy_search("   ", index)
    assert results == []


def test_results_are_question_objects(index):
    results = fuzzy_search("binary search", index)
    assert len(results) > 0
    for r in results:
        assert hasattr(r, "id")
        assert hasattr(r, "title")
        assert hasattr(r, "url")


def test_limit_parameter(index):
    results = fuzzy_search("sum", index, limit=5)
    assert len(results) <= 5
