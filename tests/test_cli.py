"""Tests for the Dooma CLI — using typer.testing.CliRunner."""

from typer.testing import CliRunner

import dooma.cli.main as cli_main
from dooma.cli.main import app

runner = CliRunner()


def _skip_home_setup(monkeypatch):
    monkeypatch.setattr(cli_main, "is_onboarded", lambda: True)
    monkeypatch.setattr(cli_main, "load_index", lambda: object())


def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert "2.0.1" in result.output


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "practice" in result.output
    assert "browse" in result.output
    assert "search" in result.output
    assert "sheet" in result.output
    assert "mock" in result.output
    assert "dashboard" in result.output


def test_search_command():
    result = runner.invoke(app, ["search", "two sum"])
    assert result.exit_code == 0


def test_question_not_found():
    result = runner.invoke(app, ["question", "nonexistent-question-xyz"])
    assert result.exit_code == 1


def test_config_show():
    result = runner.invoke(app, ["config"])
    assert result.exit_code == 0


def test_home_practice_choice_routes_to_core_runner(monkeypatch):
    _skip_home_setup(monkeypatch)
    calls = []

    def fake_run_practice(company="", difficulty="", pattern=""):
        calls.append((company, difficulty, pattern))

    monkeypatch.setattr("dooma.commands.practice.run_practice", fake_run_practice)

    result = runner.invoke(app, input="1\nq\n")

    assert result.exit_code == 0
    assert calls == [("", "", "")]
    assert "OptionInfo" not in result.output
    assert "No questions found for company" not in result.output


def test_home_sheet_choice_routes_to_core_runner(monkeypatch):
    _skip_home_setup(monkeypatch)
    calls = []

    def fake_run_sheet(sheet_id=""):
        calls.append(sheet_id)

    monkeypatch.setattr("dooma.commands.sheet.run_sheet", fake_run_sheet)

    result = runner.invoke(app, input="4\nq\n")

    assert result.exit_code == 0
    assert calls == [""]
    assert "OptionInfo" not in result.output


def test_home_mock_choice_routes_to_core_runner(monkeypatch):
    _skip_home_setup(monkeypatch)
    calls = []

    def fake_run_mock(count=5, difficulty=""):
        calls.append((count, difficulty))

    monkeypatch.setattr("dooma.commands.mock.run_mock", fake_run_mock)

    result = runner.invoke(app, input="5\nq\n")

    assert result.exit_code == 0
    assert calls == [(5, "")]
    assert "OptionInfo" not in result.output
