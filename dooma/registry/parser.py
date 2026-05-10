import json
from pathlib import Path
from typing import List, Dict, Any

# Mock catalog for v1 MVP
MOCK_CATALOG = [
    {
        "id": "two_sum",
        "title": "Two Sum",
        "difficulty": "Easy",
        "topics": ["Array", "Hash Table"],
        "companies": {
            "Amazon": {"frequency": 5},
            "Google": {"frequency": 3}
        },
        "description": "Given an array of integers nums and an integer target, return indices of the two numbers such that they add up to target.",
        "stub": "def two_sum(nums, target):\n    pass\n",
        "tests": [
            {"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]},
            {"input": {"nums": [3, 2, 4], "target": 6}, "expected": [1, 2]}
        ]
    },
    {
        "id": "number_of_islands",
        "title": "Number of Islands",
        "difficulty": "Medium",
        "topics": ["Array", "Depth-First Search", "Breadth-First Search", "Union Find", "Matrix"],
        "companies": {
            "Amazon": {"frequency": 8},
            "Google": {"frequency": 4}
        },
        "description": "Given an m x n 2D binary grid grid which represents a map of '1's (land) and '0's (water), return the number of islands.",
        "stub": "def numIslands(grid):\n    pass\n",
        "tests": [
            {"input": {"grid": [["1","1","1","1","0"],["1","1","0","1","0"],["1","1","0","0","0"],["0","0","0","0","0"]]}, "expected": 1}
        ]
    }
]

class RegistrySync:
    """Handles syncing problems from the registry into the local database."""
    
    @staticmethod
    def fetch_catalog() -> List[Dict[str, Any]]:
        """Fetches the latest catalog. Currently uses a mock for v1 MVP."""
        return MOCK_CATALOG

    @staticmethod
    def sync_to_db(db_manager):
        """Syncs the fetched catalog into the local SQLite DB and caches problem files."""
        catalog = RegistrySync.fetch_catalog()
        conn = db_manager.connect()
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
                json.dumps(problem["companies"])
            ))
            
            cache_dir = db_manager.db_path.parent / "registry" / problem["id"]
            cache_dir.mkdir(parents=True, exist_ok=True)
            
            (cache_dir / "problem.md").write_text(f"# {problem['title']}\n\n{problem['description']}")
            (cache_dir / "stub.py").write_text(problem['stub'])
            (cache_dir / ".tests.json").write_text(json.dumps(problem['tests'], indent=2))
            
        conn.commit()

class ProblemPuller:
    """Handles scaffolding a problem from the registry cache to the active folder."""
    
    @staticmethod
    def pull(problem_id: str, dooma_dir: Path, active_dir: Path) -> bool:
        """Pulls a problem by ID and scaffolds it. Returns True on success."""
        cache_dir = dooma_dir / "registry" / problem_id
        if not cache_dir.exists():
            return False
            
        target_dir = active_dir / problem_id
        target_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy files
        (target_dir / "problem.md").write_text((cache_dir / "problem.md").read_text())
        (target_dir / "solution.py").write_text((cache_dir / "stub.py").read_text())
        (target_dir / ".tests.json").write_text((cache_dir / ".tests.json").read_text())
        
        return True
