# Contributing to Dooma

First off, thank you for considering contributing to Dooma! It's people like you that make Dooma a great tool for the community.

## 1. Branching Strategy

We follow a strict GitFlow-inspired branching strategy:

- **`main`**: Production-ready code. Releases are cut from here.
- **`develop`**: The main integration branch. All feature branches merge into here.
- **`feature/*`**: For new features (e.g., `feature/spaced-repetition`).
- **`fix/*`** or **`hotfix/*`**: For urgent bug fixes.

**Always branch off `develop`** when starting a new feature, and open your Pull Request against the `develop` branch.

## 2. Development Setup

1. Fork and clone the repository:
   ```bash
   git clone https://github.com/<your-username>/dooma.git
   cd dooma
   ```
2. Checkout the develop branch: `git checkout develop`
3. Create your feature branch: `git checkout -b feature/your-feature-name`
4. Install the package locally:
   ```bash
   pip install -e .
   ```
5. Install development tools when you plan to run formatting and static checks:
   ```bash
   pip install -e ".[dev]"
   ```
6. Run the CLI locally:
   ```bash
   dooma
   ```

## 3. Code Style

We enforce standard Python formatting:
- Use `black` for code formatting.
- Use `ruff` for linting.
- Use type hints wherever possible, validated by `mypy`.

Before submitting a PR, ensure you have run:
```bash
black .
ruff check .
mypy dooma
```

## 4. Pull Request Process

1. Keep each PR focused on one bug, feature, or documentation improvement.
2. Ensure your code passes the relevant checks before pushing.
3. Update `README.md`, dataset docs, or CLI docs when your change affects user-facing behavior.
4. Use the provided PR template and link the related issue with `Fixes #<issue-number>` when applicable.
5. Respond to maintainer feedback with a follow-up commit instead of opening a duplicate PR.
