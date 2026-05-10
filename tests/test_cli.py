from typer.testing import CliRunner
from dooma.cli.main import app

runner = CliRunner(charset="utf-8")


def test_app_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Dooma: A professional developer workspace" in result.stdout


def test_init_command_creates_workspace(tmp_path, monkeypatch):
    # Change the current working directory to the temporary path for the test
    monkeypatch.chdir(tmp_path)

    result = runner.invoke(app, ["init"])
    assert result.exit_code == 0
    assert "Workspace Initialized Successfully" in result.stdout
    assert (tmp_path / ".dooma").exists()
