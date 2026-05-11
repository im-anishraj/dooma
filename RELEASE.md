# Release and Versioning Strategy

This document outlines the strict versioning rules for **Dooma** as a published open-source PyPI package.

## Semantic Versioning (`MAJOR.MINOR.PATCH`)

Dooma strictly follows [Semantic Versioning 2.0.0](https://semver.org/). All releases must conform to this standard to ensure predictability for our users.

### When to bump the **PATCH** version (e.g., `0.1.0` -> `0.1.1`)
A patch release represents backwards-compatible bug fixes and dataset updates.
- Fixing a typo in the CLI.
- Updating the `companies.json` dataset with new questions or updated URLs.
- Fixing a bug where the CLI crashes on specific inputs.
- Minor documentation improvements.

### When to bump the **MINOR** version (e.g., `0.1.0` -> `0.2.0`)
A minor release represents backwards-compatible new features.
- Adding a new command-line option (e.g., sorting by difficulty).
- Introducing a new interactive menu screen.
- Adding a new way to filter companies.
- Refactoring internal code without changing how the user interacts with the tool.

### When to bump the **MAJOR** version (e.g., `0.1.0` -> `1.0.0`)
A major release represents breaking, incompatible changes.
- Completely dropping support for an old Python version.
- Drastically changing the fundamental UI/UX flow in a way that breaks existing user expectations.
- Moving from a terminal app to a graphical app.

## Publishing Process

1. Merge your approved PR into `main`.
2. Update the `version` string in `pyproject.toml`.
3. Create a GitHub Release with the tag matching the version (e.g., `v0.2.0`).
4. GitHub Actions will automatically handle the PyPI publishing (via Trusted Publishing OIDC).
