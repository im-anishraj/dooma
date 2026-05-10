from pathlib import Path

from dooma.core.workspace import WorkspaceManager


def test_workspace_initialization(tmp_path: Path):
    workspace = WorkspaceManager(tmp_path)

    # Pre-check
    assert not workspace.is_initialized()

    # Init
    workspace.initialize()

    # Post-check
    assert workspace.is_initialized()
    assert (tmp_path / ".dooma").exists()
    assert (tmp_path / "active").exists()
    assert (tmp_path / "solved").exists()
    assert (tmp_path / "archive").exists()
    assert (tmp_path / ".dooma" / "state.db").exists()
