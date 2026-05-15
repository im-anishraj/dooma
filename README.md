# Dooma

<p align="center">
  <img alt="Dooma terminal logo" src="https://raw.githubusercontent.com/im-anishraj/dooma/main/dooma.png" width="711">
</p>

<p align="center">
  <strong>Offline-first DSA interview prep in your terminal.</strong><br>
  Search 3,310 questions, browse 17,931 company mappings, run mock sessions, and track progress locally.
</p>

<p align="center">
  <a href="https://github.com/im-anishraj/dooma/actions/workflows/ci.yml"><img alt="CI" src="https://img.shields.io/github/actions/workflow/status/im-anishraj/dooma/ci.yml?branch=main&label=ci&style=for-the-badge"></a>
  <a href="https://pypi.org/project/dooma/"><img alt="PyPI" src="https://img.shields.io/pypi/v/dooma?style=for-the-badge"></a>
  <a href="https://www.python.org/downloads/"><img alt="Python 3.9+" src="https://img.shields.io/badge/python-3.9%2B-blue?style=for-the-badge"></a>
  <a href="https://opensource.org/licenses/MIT"><img alt="MIT License" src="https://img.shields.io/badge/license-MIT-yellow?style=for-the-badge"></a>
  <a href="https://pepy.tech/project/dooma"><img alt="Downloads" src="https://img.shields.io/pepy/dt/dooma?style=for-the-badge"></a>
</p>

Dooma turns scattered interview-prep data into a focused terminal workflow. It gives you a fast way to find what companies ask, open the exact LeetCode-style problem, mark progress, keep notes, and come back later without accounts, dashboards, or network dependency after installation.

```bash
pip install dooma
dooma
```

## Why It Exists

Interview prep usually fails in the handoff between "what should I solve?" and "did I actually make progress?" Dooma keeps that loop short:

- **Company-first discovery**: see question pools for companies like Google, Amazon, Meta, Microsoft, and Bloomberg.
- **Fast local search**: jump from rough text like `two sum` or `binary tree` to matching questions.
- **Local progress tracking**: solved, attempted, skipped, bookmarks, notes, and streaks live in your own `~/.dooma` directory.
- **Offline-first runtime**: the packaged dataset ships with a prebuilt index, so the CLI does not parse thousands of YAML files on every launch.
- **Contributor-friendly data model**: canonical data stays as readable YAML; the generated runtime index is reproducible.

## At A Glance

| Area | Current state |
| --- | --- |
| Unique questions | 3,310 |
| Company-question mappings | 17,931 |
| Companies | 662 |
| Difficulty split | 808 easy, 1,757 medium, 745 hard |
| Active sheet coverage | Blind 75 has 71 mapped questions |
| Runtime index | `dooma/data/index.json`, generated from YAML |
| Local state | `~/.dooma/state.db` and `~/.dooma/config.json` |
| Python support | 3.9+ |

## Install

From PyPI:

```bash
pip install dooma
```

From source:

```bash
git clone https://github.com/im-anishraj/dooma.git
cd dooma
pip install -e ".[dev]"
```

Check the install:

```bash
dooma doctor
```

## 60-Second Tour

Launch the interactive hub:

```bash
dooma
```

The home screen gives you the main workflows:

```text
1  practice     Pattern-first question browser
2  browse       Browse patterns & companies
3  search       Fuzzy search questions
4  sheet        Curated roadmaps
5  mock         Timed mock interview
6  dashboard    Your progress stats
7  guide        Commands, workflows, and support
8  quit         Exit Dooma
```

You can also run commands directly:

```bash
dooma search "two sum"
dooma companies --limit 10
dooma question two-sum
dooma random --difficulty medium
dooma mock --count 5
dooma stats
```

## Core Workflows

### Find Company Questions

```bash
dooma companies --limit 5
dooma browse companies
dooma practice --company google
```

The company lists are sorted by available question volume. Current top pools include Google, Amazon, Meta, Microsoft, and Bloomberg.

### Search The Dataset

```bash
dooma search "two sum"
dooma search --limit 5 "binary search"
```

Search uses fuzzy title/topic matching through RapidFuzz, which makes it useful even when you only remember part of a problem name.

### Open A Specific Question

```bash
dooma question two-sum
```

Question screens show difficulty, status, URL, top companies, and local notes when present.

### Run A Mock Session

```bash
dooma mock --count 5
dooma mock --count 3 --difficulty hard
```

Mock mode samples questions, starts a timer, and lets you open, solve, or skip each prompt.

### Track Progress

```bash
dooma dashboard
dooma stats
dooma bookmarks
```

Progress is intentionally local. Dooma does not require sign-in and does not upload your activity.

## Question Actions

Inside practice, company, sheet, and random-question flows:

| Key | Action |
| --- | --- |
| `o` | Open the problem URL in your browser |
| `m` | Cycle status: `unsolved -> attempted -> solved -> skipped` |
| `b` | Bookmark or unbookmark the question |
| `n` | Add or edit a local note |
| `q` | Go back |

## Command Map

| Command | Purpose |
| --- | --- |
| `dooma` | Open the interactive command hub |
| `dooma guide` / `dooma help` | Show commands, workflows, and support links |
| `dooma version` / `dooma --version` / `dooma -V` | Print the installed version |
| `dooma doctor` | Check Python, dataset, config, and local database health |
| `dooma search <query>` | Search questions by keyword |
| `dooma question <slug>` | Open one question by slug |
| `dooma companies` | List companies with the largest question pools |
| `dooma browse companies` | Browse companies interactively |
| `dooma patterns` | List pattern taxonomy entries |
| `dooma sheets` | List available sheets |
| `dooma sheet blind-75` | Work through the mapped Blind 75 sheet |
| `dooma practice` | Browse questions interactively, optionally filtered |
| `dooma random` | Open a random filtered question |
| `dooma mock` | Start a timed random session |
| `dooma dashboard` / `dooma stats` | Show local progress |
| `dooma bookmarks` | Show bookmarked questions |
| `dooma config --reset` | Reset onboarding config |

## Data, Privacy, And Performance

Dooma has two kinds of data:

- **Packaged dataset**: YAML files in `dooma/data/` are the source of truth for questions, companies, sheets, and pattern taxonomy.
- **Runtime index**: `dooma/data/index.json` is generated from YAML so installed users get fast startup without parsing roughly 4,000 YAML files each run.
- **User state**: progress, notes, bookmarks, and streaks are stored locally in SQLite at `~/.dooma/state.db`.
- **Config**: onboarding choices live in `~/.dooma/config.json`.

The CLI is offline-first after installation. It opens problem URLs only when you ask it to open a browser.

## Current Dataset Status

The company-wise dataset is the most complete part of Dooma today. Some roadmap structures are intentionally present before their mappings are complete:

| Dataset area | Status |
| --- | --- |
| Company mappings | Active: 17,931 mappings across 662 companies |
| Questions | Active: 3,310 unique question records |
| Blind 75 | Active: 71 mapped questions |
| Pattern taxonomy | Present: 25 pattern entries |
| Pattern-tagged questions | Not populated yet |
| NeetCode 150 / Striver SDE | Sheet definitions exist, mappings are not populated yet |

This transparency matters for contributors: the highest-impact data work today is completing pattern tags and sheet mappings.

## Project Structure

```text
dooma/
  cli/              Typer app registration and home screen
  commands/         Practice, browse, search, sheet, mock, dashboard
  data/             Canonical YAML dataset plus generated index.json
  dataset/          Legacy JSON snapshot
  config.py         Local onboarding/config state
  db.py             SQLite progress, bookmarks, notes, streaks
  display.py        Rich terminal rendering and logo output
  loader.py         Prebuilt index loader with YAML fallback
  search.py         RapidFuzz search helpers
scripts/
  build_index.py    Rebuild dooma/data/index.json from YAML
  benchmark_loader.py
tests/              CLI, loader, search, display, and state tests
```

## Development

Set up a local environment:

```bash
git clone https://github.com/im-anishraj/dooma.git
cd dooma
pip install -e ".[dev]"
```

Run the core checks:

```bash
ruff check .
mypy dooma
python -m pytest
```

When dataset YAML changes, rebuild and verify the runtime index:

```bash
python scripts/build_index.py
python scripts/build_index.py --check
python scripts/benchmark_loader.py
```

Build release artifacts locally:

```bash
python -m pip install build twine
python -m build
python -m twine check dist/*
```

## Good First Contributions

The most useful contributions are practical and data-driven:

- Add missing pattern tags to questions.
- Complete NeetCode 150 and Striver SDE sheet mappings.
- Improve fuzzy-search ranking for ambiguous queries.
- Add regression tests for interactive command flows.
- Improve dataset validation scripts.
- Polish Windows, macOS, and Linux terminal rendering edge cases.

Please read [CONTRIBUTING.md](CONTRIBUTING.md) before opening a pull request. Keep PRs focused and include the relevant test or data-index check.

## What Dooma Is Not

Dooma is not a LeetCode replacement, online judge, or solution database. It does not submit code, scrape your account, or sync progress to a server. It is a fast local command center for deciding what to solve next and remembering your progress.

## Roadmap

### Dataset Coverage Priorities

We are working on expanding dataset coverage in the following order:

1. **Pattern Tags** - Add pattern-based tagging for better problem categorization
2. **NeetCode 150** - Ensure complete coverage of NeetCode 150 problems
3. **Striver SDE Sheet** - Add support for Striver's SDE preparation problems
4. **Validation Improvements** - Enhance dataset validation and quality checks

### Current Gaps

- Pattern tags are incomplete for some problem categories
- NeetCode 150 coverage needs expansion
- Striver SDE sheet integration is in early stages
- Validation needs improvement for edge cases

### Related Issues

- See issues tagged with `area:data` for specific dataset tasks
- Check `area:docs` for documentation improvements

> **Note:** Timelines depend on contributor availability. We do not guarantee specific release dates.


## Release And Maintenance

Releases are versioned in `pyproject.toml` and published to PyPI from GitHub Releases through the repository publish workflow. See [RELEASE.md](RELEASE.md) for versioning rules.

Community expectations are documented in [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md). The project is released under the [MIT License](LICENSE).
