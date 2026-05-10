import sqlite3
from pathlib import Path
import pytest
from dooma.db.manager import DatabaseManager


@pytest.fixture
def temp_db_path(tmp_path: Path) -> Path:
    """Provides a temporary file path for the test database."""
    return tmp_path / ".dooma" / "state.db"


def test_database_manager_initialization(temp_db_path: Path):
    """Test that the database manager properly creates the DB and tables."""
    db = DatabaseManager(temp_db_path)
    db.initialize_schema()

    # Assert DB file is created on the filesystem
    assert temp_db_path.exists()

    conn = db.connect()
    cursor = conn.cursor()

    # Check if tables exist
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = {row["name"] for row in cursor.fetchall()}

    assert "problems" in tables
    assert "progress" in tables
    assert "campaigns" in tables

    db.close()
