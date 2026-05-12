"""SQLite state layer — manages ~/.dooma/state.db for user progress.

All user state (solve status, bookmarks, notes, sessions, streaks) lives
here.  The question *content* lives in YAML files; this module only tracks
the user's interaction with that content.
"""

from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from pathlib import Path

_DB_PATH = Path.home() / ".dooma" / "state.db"
_conn: sqlite3.Connection | None = None

_SCHEMA = """
CREATE TABLE IF NOT EXISTS question_status (
    question_id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'unsolved',
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS bookmarks (
    question_id TEXT PRIMARY KEY,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS notes (
    question_id TEXT PRIMARY KEY,
    content TEXT NOT NULL,
    updated_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    mode TEXT,
    questions_attempted INTEGER DEFAULT 0,
    start_time TEXT,
    end_time TEXT
);

CREATE TABLE IF NOT EXISTS streaks (
    date TEXT PRIMARY KEY,
    questions_solved INTEGER DEFAULT 0
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _today() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d")


def get_connection(db_path: Path | None = None) -> sqlite3.Connection:
    """Return (and cache) the SQLite connection, creating tables on first use."""
    global _conn
    if _conn is not None and db_path is None:
        return _conn

    path = db_path or _DB_PATH
    path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(path))
    conn.row_factory = sqlite3.Row
    conn.executescript(_SCHEMA)

    if db_path is None:
        _conn = conn
    return conn


def close():
    """Close the cached connection (if any)."""
    global _conn
    if _conn is not None:
        _conn.close()
        _conn = None


# ── Status ──────────────────────────────────────────────────────────────────

def get_status(question_id: str, *, conn: sqlite3.Connection | None = None) -> str:
    """Return the status for a question (default: 'unsolved')."""
    c = conn or get_connection()
    row = c.execute(
        "SELECT status FROM question_status WHERE question_id = ?", (question_id,)
    ).fetchone()
    return row["status"] if row else "unsolved"


def set_status(question_id: str, status: str, *, conn: sqlite3.Connection | None = None) -> None:
    """Set the status for a question."""
    c = conn or get_connection()
    c.execute(
        "INSERT INTO question_status (question_id, status, updated_at) VALUES (?, ?, ?) "
        "ON CONFLICT(question_id) DO UPDATE SET status = excluded.status, updated_at = excluded.updated_at",
        (question_id, status, _now()),
    )
    c.commit()


def get_all_statuses(*, conn: sqlite3.Connection | None = None) -> dict[str, str]:
    """Return a dict of question_id → status for all tracked questions."""
    c = conn or get_connection()
    rows = c.execute("SELECT question_id, status FROM question_status").fetchall()
    return {r["question_id"]: r["status"] for r in rows}


# ── Bookmarks ───────────────────────────────────────────────────────────────

def toggle_bookmark(question_id: str, *, conn: sqlite3.Connection | None = None) -> bool:
    """Toggle bookmark.  Returns True if now bookmarked, False if removed."""
    c = conn or get_connection()
    existing = c.execute(
        "SELECT 1 FROM bookmarks WHERE question_id = ?", (question_id,)
    ).fetchone()
    if existing:
        c.execute("DELETE FROM bookmarks WHERE question_id = ?", (question_id,))
        c.commit()
        return False
    else:
        c.execute(
            "INSERT INTO bookmarks (question_id, created_at) VALUES (?, ?)",
            (question_id, _now()),
        )
        c.commit()
        return True


def is_bookmarked(question_id: str, *, conn: sqlite3.Connection | None = None) -> bool:
    """Check if a question is bookmarked."""
    c = conn or get_connection()
    return c.execute(
        "SELECT 1 FROM bookmarks WHERE question_id = ?", (question_id,)
    ).fetchone() is not None


# ── Notes ───────────────────────────────────────────────────────────────────

def get_note(question_id: str, *, conn: sqlite3.Connection | None = None) -> str | None:
    """Return the note content for a question, or None."""
    c = conn or get_connection()
    row = c.execute(
        "SELECT content FROM notes WHERE question_id = ?", (question_id,)
    ).fetchone()
    return row["content"] if row else None


def set_note(question_id: str, content: str, *, conn: sqlite3.Connection | None = None) -> None:
    """Create or update a note for a question."""
    c = conn or get_connection()
    c.execute(
        "INSERT INTO notes (question_id, content, updated_at) VALUES (?, ?, ?) "
        "ON CONFLICT(question_id) DO UPDATE SET content = excluded.content, updated_at = excluded.updated_at",
        (question_id, content, _now()),
    )
    c.commit()


# ── Streaks ─────────────────────────────────────────────────────────────────

def get_streak_today(*, conn: sqlite3.Connection | None = None) -> int:
    """Return the number of questions solved today."""
    c = conn or get_connection()
    row = c.execute(
        "SELECT questions_solved FROM streaks WHERE date = ?", (_today(),)
    ).fetchone()
    return row["questions_solved"] if row else 0


def increment_streak_today(*, conn: sqlite3.Connection | None = None) -> None:
    """Increment the streak counter for today."""
    c = conn or get_connection()
    c.execute(
        "INSERT INTO streaks (date, questions_solved) VALUES (?, 1) "
        "ON CONFLICT(date) DO UPDATE SET questions_solved = questions_solved + 1",
        (_today(),),
    )
    c.commit()


# ── Dashboard ───────────────────────────────────────────────────────────────

def get_dashboard_stats(*, conn: sqlite3.Connection | None = None) -> dict:
    """Return aggregate stats for the dashboard command."""
    c = conn or get_connection()

    statuses = get_all_statuses(conn=c)
    solved = sum(1 for s in statuses.values() if s == "solved")
    attempted = sum(1 for s in statuses.values() if s == "attempted")
    skipped = sum(1 for s in statuses.values() if s == "skipped")

    bookmarks_count = c.execute("SELECT COUNT(*) as cnt FROM bookmarks").fetchone()["cnt"]
    notes_count = c.execute("SELECT COUNT(*) as cnt FROM notes").fetchone()["cnt"]
    streak_today = get_streak_today(conn=c)

    # Streak length (consecutive days ending today)
    streak_days = 0
    rows = c.execute("SELECT date FROM streaks WHERE questions_solved > 0 ORDER BY date DESC").fetchall()
    from datetime import timedelta
    today = datetime.now(timezone.utc).date()
    for row in rows:
        d = datetime.strptime(row["date"], "%Y-%m-%d").date()
        expected = today - timedelta(days=streak_days)
        if d == expected:
            streak_days += 1
        else:
            break

    return {
        "solved": solved,
        "attempted": attempted,
        "skipped": skipped,
        "total_tracked": len(statuses),
        "bookmarks": bookmarks_count,
        "notes": notes_count,
        "streak_today": streak_today,
        "streak_days": streak_days,
    }
