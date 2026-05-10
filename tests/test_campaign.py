from pathlib import Path
from typer.testing import CliRunner
from dooma.cli.main import app
from dooma.db.manager import DatabaseManager


runner = CliRunner(charset="utf-8")


def test_prep_campaign(tmp_path: Path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    
    # Init workspace
    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    
    # Start campaign
    result = runner.invoke(app, ["prep", "start", "Amazon"])
    assert result.exit_code == 0
    assert "Started preparation campaign for Amazon" in result.stdout
    
    # Pull next
    result = runner.invoke(app, ["prep", "next"])
    assert result.exit_code == 0
    assert "Successfully pulled Two Sum for Amazon" in result.stdout
    
    # Verify in DB
    db = DatabaseManager(tmp_path / ".dooma" / "state.db")
    conn = db.connect()
    cursor = conn.cursor()
    cursor.execute("SELECT target_company FROM campaigns")
    assert cursor.fetchone()["target_company"] == "Amazon"
    db.close()
