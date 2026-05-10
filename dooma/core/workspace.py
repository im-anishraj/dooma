from pathlib import Path
import json
from dooma.db.manager import DatabaseManager
from dooma.dataset.loader import DatasetLoader


class WorkspaceManager:
    """Handles the creation and management of the Dooma workspace structure."""

    def __init__(self, root_dir: Path):
        self.root_dir = root_dir
        self.dooma_dir = self.root_dir / ".dooma"
        self.active_dir = self.root_dir / "active"
        self.solved_dir = self.root_dir / "solved"
        self.archive_dir = self.root_dir / "archive"

    def initialize(self):
        """Scaffolds the workspace directories and initializes the database."""
        # Create directories
        self.dooma_dir.mkdir(parents=True, exist_ok=True)
        self.active_dir.mkdir(parents=True, exist_ok=True)
        self.solved_dir.mkdir(parents=True, exist_ok=True)
        self.archive_dir.mkdir(parents=True, exist_ok=True)

        # Initialize SQLite DB
        db_path = self.dooma_dir / "state.db"
        db = DatabaseManager(db_path)
        db.initialize_schema()
        
        # Instantly load the packaged dataset catalog
        catalog = DatasetLoader.fetch_catalog()
        conn = db.connect()
        cursor = conn.cursor()
        for problem in catalog:
            cursor.execute("""
                INSERT OR REPLACE INTO problems (id, title, difficulty, topics, companies)
                VALUES (?, ?, ?, ?, ?)
            """, (
                problem["id"],
                problem["title"],
                problem["difficulty"],
                json.dumps(problem["topics"]),
                json.dumps(problem.get("companies", {}))
            ))
        conn.commit()
        db.close()

    def is_initialized(self) -> bool:
        """Checks if the workspace is already initialized."""
        return self.dooma_dir.exists() and (self.dooma_dir / "state.db").exists()
