# Dooma

![Dooma Logo](https://img.shields.io/badge/Dooma-DSA_Forge-blue?style=for-the-badge)
[![PyPI version](https://badge.fury.io/py/dooma.svg)](https://badge.fury.io/py/dooma)
[![Downloads](https://pepy.tech/badge/dooma)](https://pepy.tech/project/dooma)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Dooma** is your terminal-first Data Structures and Algorithms (DSA) preparation companion. It serves as a lightweight, interactive explorer for **17,900+ company-question mappings** across **660+ top tech companies**.

No more scrolling through clunky websites or losing track of which questions Amazon or Google actually ask. Dooma brings the entire dataset straight into your console with a beautiful, responsive UI.

## Features

- **Massive Database**: Access a curated, offline-first dataset of 17,931 question mappings across 662 companies.
- **Interactive Terminal UI**: Built with `Rich` and `Typer`, Dooma offers a paginated command hub for practice, browsing, search, sheets, mock interviews, and progress.
- **Company and Pattern Browser**: Browse company-specific and pattern-specific question lists, then open, bookmark, mark status, or add notes to questions.
- **Data Rich**: Instantly see question titles, difficulty ratings, frequency tiers, status, and direct LeetCode URLs.
- **Zero Overhead**: No accounts, no internet required to browse the database, no tracking. Just pure preparation.

## Quickstart

Dooma is incredibly easy to set up and use. 

### Installation
Clone the repository and install it locally using `pip`:
```bash
git clone https://github.com/im-anishraj/dooma.git
cd dooma
pip install -e .
```

### Usage
Once installed, simply run the tool from anywhere in your terminal:
```bash
dooma
```
1. Complete the one-time onboarding prompts on first launch.
2. Use the main menu to choose practice, browse, search, sheets, mock interview, or dashboard.
3. Use `dooma browse companies` to browse company-specific lists, or `dooma search "two sum"` to jump straight to matching questions.
4. Type `q` or `0` where shown to safely back out of menus.

## Contributing

We welcome contributions to make Dooma even better! Whether you want to update the dataset, add new features, or improve the UI, we'd love your help.
Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started and the pull request process.

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
