# Dooma

<p align="center">
  <strong>The offline terminal atlas for DSA interview preparation.</strong>
</p>

<p align="center">
  <a href="https://pypi.org/project/dooma/"><img alt="PyPI" src="https://img.shields.io/pypi/v/dooma?style=for-the-badge"></a>
  <a href="https://www.python.org/downloads/"><img alt="Python 3.9+" src="https://img.shields.io/badge/python-3.9%2B-blue?style=for-the-badge"></a>
  <a href="https://opensource.org/licenses/MIT"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-yellow?style=for-the-badge"></a>
  <a href="https://pepy.tech/project/dooma"><img alt="Downloads" src="https://img.shields.io/pepy/dt/dooma?style=for-the-badge"></a>
</p>

```text
██████╗  ██████╗  ██████╗ ███╗   ███╗ █████╗
██╔══██╗██╔═══██╗██╔═══██╗████╗ ████║██╔══██╗
██║  ██║██║   ██║██║   ██║██╔████╔██║███████║
██║  ██║██║   ██║██║   ██║██║╚██╔╝██║██╔══██║
██████╔╝╚██████╔╝╚██████╔╝██║ ╚═╝ ██║██║  ██║
╚═════╝  ╚═════╝  ╚═════╝ ╚═╝     ╚═╝╚═╝  ╚═╝
terminal DSA forge • 17,931 interview mappings • offline first
```

Dooma brings company-wise LeetCode-style preparation into your terminal: searchable, bookmarkable, trackable, and available without accounts or network access after install.

## Why Dooma

Interview prep breaks down when the data is scattered, noisy, or trapped behind a browser tab you never meant to open for an hour. Dooma keeps the loop tight:

- Find what a company asks.
- Pick a pattern or roadmap.
- Open the exact problem.
- Mark progress, keep notes, and come back tomorrow.

No dashboards to sign into. No hidden telemetry. No spreadsheet archaeology.

## Dataset At A Glance

| Metric | Count |
| --- | ---: |
| Unique questions | 3,310 |
| Company-question mappings | 17,931 |
| Companies | 662 |
| DSA patterns | 25 |
| Curated sheets | 3 |

The active app dataset lives in `dooma/data/` as YAML files. Releases also ship a generated `dooma/data/index.json` runtime index so startup does not parse thousands of YAML files on every launch. The package includes a legacy JSON snapshot under `dooma/dataset/`.

## Features

| Feature | What it gives you |
| --- | --- |
| Company browser | Paginated company lists sorted by available question volume. |
| Pattern practice | Practice by DSA pattern such as binary search, graph, heap, or sliding window. |
| Fuzzy search | Jump from rough text like `two sum` or `binary tree` to matching questions. |
| Curated sheets | Work through Blind 75, NeetCode 150, and Striver SDE style roadmaps. |
| Mock mode | Generate a timed random interview set with optional difficulty filtering. |
| Local progress | Track solved, attempted, skipped, bookmarks, notes, and streaks in SQLite. |
| Offline-first | Browse the bundled dataset without internet after installation. |

## Install

From PyPI:

```bash
pip install dooma
```

From source:

```bash
git clone https://github.com/im-anishraj/dooma.git
cd dooma
pip install -e .
```

Dooma supports Python 3.9 and newer.

## Quick Start

Launch the interactive terminal app:

```bash
dooma
```

First launch asks a short onboarding flow, then opens the command hub:

```text
Commands:
  1  practice     Pattern-first question browser
  2  browse       Browse patterns & companies
  3  search       Fuzzy search questions
  4  sheet        Curated roadmaps
  5  mock         Timed mock interview
  6  dashboard    Your progress stats
  7  help         Command guide & workflows
  8  quit         Exit Dooma
```

Inside the menu, you can type the number, the command name, or shell-style input such as `dooma help` and `dooma version`.

## Command Examples

Check the installed version:

```bash
dooma --version
dooma -V
dooma version
```

Open the built-in guide:

```bash
dooma help
dooma guide
```

Search for a problem:

```bash
dooma search "two sum"
dooma search --limit 5 "binary search"
```

Open a question detail screen:

```bash
dooma question two-sum
```

Browse company-wise questions:

```bash
dooma browse companies
dooma companies
dooma companies --limit 50
```

List patterns and sheets:

```bash
dooma patterns
dooma sheets
```

Practice by filters:

```bash
dooma practice --company google
dooma practice --difficulty medium
dooma practice --pattern sliding-window
```

Work through a sheet:

```bash
dooma sheet blind-75
dooma sheet neetcode-150
dooma sheet striver-sde
```

Start a mock interview:

```bash
dooma mock --count 5
dooma mock --count 3 --difficulty hard
```

View progress:

```bash
dooma dashboard
dooma stats
dooma bookmarks
```

Reset onboarding/config:

```bash
dooma config --reset
```

Check your installation:

```bash
dooma doctor
```

## Question Actions

Inside question detail views, Dooma supports:

| Key | Action |
| --- | --- |
| `o` | Open the LeetCode URL in your browser. |
| `m` | Cycle status: unsolved -> attempted -> solved -> skipped. |
| `b` | Toggle bookmark. |
| `n` | Add or edit a note. |
| `q` | Go back. |

Progress is stored locally in `~/.dooma/state.db`.

## Project Layout

```text
dooma/
  cli/              Typer app registration and home screen
  commands/         Command implementations
  data/             Active YAML dataset plus generated runtime index.json
  dataset/          Legacy JSON snapshot
  config.py         Local config and onboarding state
  db.py             SQLite progress, notes, bookmarks, streaks
  display.py        Rich rendering helpers and terminal wordmark
  loader.py         Prebuilt index loader with YAML fallback
  search.py         RapidFuzz search
scripts/
  build_index.py    Rebuild dooma/data/index.json from YAML
  benchmark_loader.py
tests/              CLI, loader, search, and state tests
```

## Development

Install development tools:

```bash
pip install -e ".[dev]"
```

Run the release checks:

```bash
ruff check .
mypy dooma
python -m pytest
```

Rebuild and verify the packaged runtime index after changing dataset YAML:

```bash
python scripts/build_index.py
python scripts/build_index.py --check
python scripts/benchmark_loader.py
```

Build a wheel locally:

```bash
python -m pip wheel . --no-deps -w dist
```

## Data Contributions

When updating data, keep references internally consistent:

- Every question must have `id`, `title`, and `url`.
- Difficulty should be `easy`, `medium`, `hard`, or empty when unknown.
- Company, pattern, and sheet references should point to existing YAML IDs.
- Keep generated caches, coverage files, and packaging artifacts out of git.

## Philosophy

Dooma is intentionally small: a fast terminal interface, a local dataset, and local progress tracking. The goal is not to replace LeetCode. The goal is to remove friction before you practice.

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](CONTRIBUTING.md), follow the existing command/data structure, and keep pull requests focused.

This project follows the [Code of Conduct](CODE_OF_CONDUCT.md).

## License

Dooma is released under the [MIT License](LICENSE).
