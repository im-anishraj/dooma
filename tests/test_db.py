"""Tests for dooma.db — SQLite state layer."""

import pytest
from dooma import db


@pytest.fixture
def conn(tmp_path):
    """Create a temporary SQLite database for each test."""
    db_path = tmp_path / "test_state.db"
    connection = db.get_connection(db_path)
    yield connection
    connection.close()


def test_set_and_get_status(conn):
    db.set_status("two-sum", "solved", conn=conn)
    assert db.get_status("two-sum", conn=conn) == "solved"


def test_get_status_default(conn):
    assert db.get_status("nonexistent", conn=conn) == "unsolved"


def test_set_status_update(conn):
    db.set_status("two-sum", "attempted", conn=conn)
    db.set_status("two-sum", "solved", conn=conn)
    assert db.get_status("two-sum", conn=conn) == "solved"


def test_toggle_bookmark_first_call(conn):
    result = db.toggle_bookmark("two-sum", conn=conn)
    assert result is True


def test_toggle_bookmark_second_call(conn):
    db.toggle_bookmark("two-sum", conn=conn)  # bookmark
    result = db.toggle_bookmark("two-sum", conn=conn)  # unbookmark
    assert result is False


def test_is_bookmarked(conn):
    assert db.is_bookmarked("two-sum", conn=conn) is False
    db.toggle_bookmark("two-sum", conn=conn)
    assert db.is_bookmarked("two-sum", conn=conn) is True


def test_set_and_get_note(conn):
    db.set_note("two-sum", "Use hash map approach", conn=conn)
    assert db.get_note("two-sum", conn=conn) == "Use hash map approach"


def test_get_note_default(conn):
    assert db.get_note("nonexistent", conn=conn) is None


def test_get_all_statuses(conn):
    db.set_status("q1", "solved", conn=conn)
    db.set_status("q2", "attempted", conn=conn)
    statuses = db.get_all_statuses(conn=conn)
    assert statuses["q1"] == "solved"
    assert statuses["q2"] == "attempted"


def test_streak_today(conn):
    assert db.get_streak_today(conn=conn) == 0
    db.increment_streak_today(conn=conn)
    assert db.get_streak_today(conn=conn) == 1
    db.increment_streak_today(conn=conn)
    assert db.get_streak_today(conn=conn) == 2


def test_get_dashboard_stats(conn):
    db.set_status("q1", "solved", conn=conn)
    db.set_status("q2", "attempted", conn=conn)
    db.set_status("q3", "skipped", conn=conn)
    db.toggle_bookmark("q1", conn=conn)
    db.set_note("q1", "test note", conn=conn)

    stats = db.get_dashboard_stats(conn=conn)
    assert "solved" in stats
    assert "attempted" in stats
    assert "skipped" in stats
    assert "bookmarks" in stats
    assert "notes" in stats
    assert "streak_today" in stats
    assert "streak_days" in stats
    assert stats["solved"] == 1
    assert stats["attempted"] == 1
    assert stats["skipped"] == 1
    assert stats["bookmarks"] == 1
    assert stats["notes"] == 1
