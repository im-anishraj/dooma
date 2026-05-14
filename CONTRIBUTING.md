# Contributing to Dooma

First off, thank you for considering contributing to Dooma! It's people like you that make Dooma a great tool for the community.

## 1. Branching Strategy

Dooma uses short-lived feature and fix branches with `main` as the release branch:

- **`main`**: Production-ready code. Releases are cut from here.
- **`feature/*`** or **`codex/*`**: Focused feature branches.
- **`fix/*`** or **`hotfix/*`**: Focused bug-fix branches.

Branch from `main` unless a maintainer asks you to target another branch.

## 2. Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/<your-username>/dooma.git
   cd dooma
   ```
2. Create your feature branch: `git checkout -b feature/your-feature-name`
3. Install the package with development tools:
   ```bash
   pip install -e ".[dev]"
   ```
4. Run the CLI locally:
   ```bash
   dooma
   ```

## 3. Code Style

We enforce standard Python formatting:
- Use `black` for code formatting.
- Use `ruff` for linting.
- Use type hints wherever possible, validated by `mypy`.

Before submitting a PR, run:
```bash
ruff check .
mypy dooma
python -m pytest
```

If you changed any dataset YAML under `dooma/data/`, also run:

```bash
python scripts/build_index.py
python scripts/build_index.py --check
```

## 4. Pull Request Process

1. Keep each PR focused on one bug, feature, or documentation improvement.
2. Ensure your code passes the relevant checks before pushing.
3. Update `README.md`, dataset docs, or CLI docs when your change affects user-facing behavior.
4. Use the provided PR template and link the related issue with `Fixes #<issue-number>` when applicable.
5. Respond to maintainer feedback with a follow-up commit instead of opening a duplicate PR.
