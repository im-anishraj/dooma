import sqlite3
from pathlib import Path
from typing import Optional


class DatabaseManager:
    """Manages the local SQLite database for Dooma."""

    def __init__(self, db_path: Path):
        """
        Initialize the database manager with a path to the SQLite file.
        """
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        """Establishes and returns a connection to the SQLite database."""
        if not self.conn:
            # Ensure the parent directory exists
            self.db_path.parent.mkdir(parents=True, exist_ok=True)
            self.conn = sqlite3.connect(self.db_path)
            # Access columns by name
            self.conn.row_factory = sqlite3.Row
            # Enable foreign keys for referential integrity
            self.conn.execute("PRAGMA foreign_keys = ON")
        return self.conn

    def close(self):
        """Closes the active database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None

    def initialize_schema(self):
        """Initializes the database tables if they do not exist."""
        conn = self.connect()
        cursor = conn.cursor()

        # Schema Version Tracking
        cursor.execute(
            "CREATE TABLE IF NOT EXISTS meta (key TEXT PRIMARY KEY, value TEXT)"
        )
        cursor.execute(
            "INSERT OR IGNORE INTO meta (key, value) VALUES ('schema_version', '1')"
        )

        # Table: Problems (Metadata downloaded from registry)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS problems (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                difficulty TEXT NOT NULL,
                topics TEXT, -- Stored as JSON string
                companies TEXT -- Stored as JSON string
            )
            """
        )

        # Table: Progress (User's local state)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS progress (
                problem_id TEXT PRIMARY KEY,
                status TEXT NOT NULL DEFAULT 'active', -- active, solved, archived
                attempts INTEGER DEFAULT 0,
                solved_at TIMESTAMP,
                time_taken_ms INTEGER,
                FOREIGN KEY (problem_id) REFERENCES problems (id)
            )
            """
        )

        # Table: Campaigns (Company prep tracking)
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS campaigns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                target_company TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )

        conn.commit()
