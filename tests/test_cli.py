"""Tests for the Dooma CLI — using typer.testing.CliRunner."""

from typer.testing import CliRunner

import dooma.cli.main as cli_main
from dooma import __version__
from dooma.cli.main import app

runner = CliRunner()


def _skip_home_setup(monkeypatch):
    monkeypatch.setattr(cli_main, "is_onboarded", lambda: True)
    monkeypatch.setattr(cli_main, "load_index", lambda: object())


def test_version_command():
    result = runner.invoke(app, ["version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_global_version_flag():
    result = runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_global_short_version_flag():
    result = runner.invoke(app, ["-V"])
    assert result.exit_code == 0
    assert __version__ in result.output


def test_help():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "practice" in result.output
    assert "browse" in result.output
    assert "search" in result.output
    assert "sheet" in result.output
    assert "mock" in result.output
    assert "dashboard" in result.output
    assert "doctor" in result.output
    assert "help" in result.output
    assert "guide" in result.output
    assert "random" in result.output
    assert "bookmarks" in result.output
    assert "stats" in result.output
    assert "companies" in result.output
    assert "patterns" in result.output
    assert "sheets" in result.output


def test_guide_command():
    result = runner.invoke(app, ["guide"])
    assert result.exit_code == 0
    assert "Essential Commands" in result.output
    assert "Support Dooma" in result.output
    assert "https://github.com/im-anishraj/dooma" in result.output
    assert "CONTRIBUTING.md" in result.output
    assert "issues" in result.output


def test_help_alias_command():
    result = runner.invoke(app, ["help"])
    assert result.exit_code == 0
    assert "Essential Commands" in result.output
    assert "Support Dooma" in result.output


def test_companies_command():
    result = runner.invoke(app, ["companies", "--limit", "3"])
    assert result.exit_code == 0
    assert "Companies" in result.output


def test_patterns_command():
    result = runner.invoke(app, ["patterns"])
    assert result.exit_code == 0
    assert "Patterns" in result.output


def test_sheets_command():
    result = runner.invoke(app, ["sheets"])
    assert result.exit_code == 0
    assert "Sheets" in result.output


def test_stats_command():
    result = runner.invoke(app, ["stats"])
    assert result.exit_code == 0
    assert "Total questions in database" in result.output


def test_bookmarks_empty(monkeypatch):
    monkeypatch.setattr(cli_main.db, "get_bookmarked_question_ids", lambda: [])
    result = runner.invoke(app, ["bookmarks"])
    assert result.exit_code == 0
    assert "No bookmarks yet" in result.output


def test_doctor_command():
    result = runner.invoke(app, ["doctor"])
    assert result.exit_code == 0
    assert "Dooma Doctor" in result.output
    assert "All checks passed" in result.output
    assert "https://github.com/im-anishraj/dooma/issues" in result.output


def test_random_command(monkeypatch):
    calls = []

    def fake_question_actions(question, statuses):
        calls.append((question.id, statuses))

    monkeypatch.setattr("dooma.commands.practice._question_actions", fake_question_actions)

    result = runner.invoke(app, ["random", "--difficulty", "easy"])
    assert result.exit_code == 0
    assert calls


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


def test_home_help_choice_shows_guide(monkeypatch):
    _skip_home_setup(monkeypatch)

    result = runner.invoke(app, input="7\n\n8\n")

    assert result.exit_code == 0
    assert "Essential Commands" in result.output
    assert "Support Dooma" in result.output


def test_home_shell_style_help_choice_shows_guide(monkeypatch):
    _skip_home_setup(monkeypatch)

    result = runner.invoke(app, input="dooma help\n\n8\n")

    assert result.exit_code == 0
    assert "Essential Commands" in result.output


def test_home_shell_style_guide_choice_shows_guide(monkeypatch):
    _skip_home_setup(monkeypatch)

    result = runner.invoke(app, input="dooma guide\n\n8\n")

    assert result.exit_code == 0
    assert "Essential Commands" in result.output
    assert "Support Dooma" in result.output


def test_home_shell_style_version_choice_prints_version(monkeypatch):
    _skip_home_setup(monkeypatch)

    result = runner.invoke(app, input="dooma version\n\n8\n")

    assert result.exit_code == 0
    assert f"dooma {__version__}" in result.output
