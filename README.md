# Dooma

![Dooma Logo](https://img.shields.io/badge/Dooma-DSA_Forge-blue?style=for-the-badge)
[![PyPI version](https://badge.fury.io/py/dooma.svg)](https://badge.fury.io/py/dooma)
[![Downloads](https://pepy.tech/badge/dooma)](https://pepy.tech/project/dooma)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Dooma** is your ultimate, blazing-fast Data Structures and Algorithms (DSA) preparation companion. Built entirely for the terminal, it serves as a lightweight, interactive explorer for over **17,900+ real interview questions** from **660+ top tech companies**.

No more scrolling through clunky websites or losing track of which questions Amazon or Google actually ask. Dooma brings the entire dataset straight into your console with a beautiful, responsive UI.

## 🚀 Features

- **Massive Database**: Access a curated, offline-first dataset of 17,931 question mappings across 662 companies.
- **Interactive Terminal UI**: Built with `Rich` and `Typer`, Dooma offers a stunning, paginated, and easy-to-navigate interface.
- **Alphabetical Explorer**: Quickly jump to your target company (e.g., press `G` for Google) and view all associated questions.
- **Data Rich**: Instantly see Question Titles, Difficulty Ratings (color-coded), Frequency/Acceptance percentages, and direct LeetCode URLs.
- **Zero Overhead**: No accounts, no internet required to browse the database, no tracking. Just pure preparation.


## 🛠️ Tech Stack

| Category | Technology |
|----------|-------------|
| Language | Python |
| CLI Framework | Typer |
| Terminal UI | Rich |
| Data Handling | JSON Dataset Processing |

---

## ⚙️ Workflow / How It Works

Dooma follows a lightweight interactive CLI workflow:

1. The user launches the application using the `dooma` command.
2. The local dataset containing company-question mappings is loaded.
3. The CLI processes and filters interview question data dynamically.
4. Rich renders an interactive terminal-based UI with formatted output and navigation support.
5. Users can browse companies, interview questions, difficulty levels, and practice links directly from the terminal.

---


## 🧩 Basic Project Structure

```text
dooma/
├── .github/             # GitHub workflows and issue templates
├── dooma/               # Core application package
│   ├── cli/             # CLI commands and navigation logic
│   ├── dataset/         # Company-question datasets
│   ├── db/              # Database/cache related utilities
│   └── __init__.py
├── scripts/             # Dataset build and utility scripts
├── pyproject.toml       # Project configuration and dependencies
├── README.md            # Project documentation
└── RELEASES.md          # Release notes and changelog
```

---

## 🔄 High-Level Workflow

```text
User Command
     │
     ▼
Load Dataset
     │
     ▼
Filter Companies / Questions
     │
     ▼
Render Rich Terminal UI
     │
     ▼
Interactive Navigation
```


## 📦 Quickstart

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
1. You will be greeted by an alphabet menu. Type the first letter of your target company (e.g., `A` for Amazon).
2. Select your company from the beautifully paginated list.
3. Browse the questions, take note of the difficulties and frequencies, and click the URLs to practice!
4. Type `0` at any time to safely step back through the menus.

## 🤝 Contributing

We welcome contributions to make Dooma even better! Whether you want to update the dataset, add new features, or improve the UI, we'd love your help.
Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started and the pull request process.

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## 📜 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
