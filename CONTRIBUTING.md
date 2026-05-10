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

1. Fork and clone the repository.
2. Checkout the develop branch: `git checkout develop`
3. Create your feature branch: `git checkout -b feature/your-feature-name`
4. Install dependencies: `pip install -e ".[dev]"`
5. Run tests: `pytest`

## 3. Code Style

We enforce standard Python formatting:
- Use `black` for code formatting.
- Use `flake8` for linting.
- Use type hints wherever possible, validated by `mypy`.

Before submitting a PR, ensure you have run:
```bash
black .
flake8 .
mypy dooma
```

## 4. Pull Request Process

1. Ensure your code passes all tests and styling checks.
2. Update the README.md or relevant documentation if you are adding new commands or features.
3. Open a Pull Request using the provided PR template.
4. Wait for a maintainer to review and approve your changes.
