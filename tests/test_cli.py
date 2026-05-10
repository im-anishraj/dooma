import pytest
from dooma.cli.main import load_data, app
from typer.testing import CliRunner

runner = CliRunner()

def test_load_data():
    """Test that the dataset loads correctly and contains expected companies."""
    data = load_data()
    assert isinstance(data, dict), "Dataset should be a dictionary"
    assert len(data) > 0, "Dataset should not be empty"
    assert "amazon" in data, "Amazon should be in the dataset"
    assert "google" in data, "Google should be in the dataset"

def test_app_help():
    """Test that the Typer app initializes and displays help."""
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Usage" in result.stdout
