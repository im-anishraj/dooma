import json
from pathlib import Path
from dooma.registry.parser import RegistrySync, ProblemPuller
from dooma.db.manager import DatabaseManager


def test_sync_and_pull(tmp_path: Path):
    dooma_dir = tmp_path / ".dooma"
    dooma_dir.mkdir(parents=True)
    active_dir = tmp_path / "active"
    active_dir.mkdir(parents=True)
    
    db_path = dooma_dir / "state.db"
    db = DatabaseManager(db_path)
    db.initialize_schema()
    
    # Test Sync
    RegistrySync.sync_to_db(db)
    
    # Check DB was populated
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM problems")
    count = cursor.fetchone()[0]
    assert count > 0
    db.close()
    
    # Check cache was created
    assert (dooma_dir / "registry" / "two_sum").exists()
    assert (dooma_dir / "registry" / "two_sum" / ".tests.json").exists()
    
    # Test Pull
    success = ProblemPuller.pull("two_sum", dooma_dir, active_dir)
    assert success is True
    
    # Check active directory
    target_dir = active_dir / "two_sum"
    assert target_dir.exists()
    assert (target_dir / "problem.md").exists()
    assert (target_dir / "solution.py").exists()
    assert (target_dir / ".tests.json").exists()
