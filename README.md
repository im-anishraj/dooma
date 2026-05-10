# Dooma

![Dooma Logo](https://img.shields.io/badge/Dooma-DSA_Forge-blue?style=for-the-badge)
[![Python Version](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

**Dooma** is a professional, open-source Python library and CLI tool designed for Data Structures and Algorithms (DSA) practice.

Instead of a messy folder of random `.py` or `.cpp` files, Dooma creates a **structured, local-first workspace**. It acts as a hybrid between a package manager (pulling questions), a test runner (verifying solutions), and a progress tracker (monitoring stats and company-wise readiness).

## Core Features

- **CLI-First**: Native, fast, and terminal-friendly operations.
- **Local SQLite Tracking**: All your progress, attempts, and stats are stored locally.
- **Company-Wise Campaigns**: Prepare for specific companies (e.g., Google, Amazon) using smart algorithms that track your readiness.
- **Automated Workflows**: Write your solution and let Dooma test it and move it to `solved/` automatically upon success.
- **Python-Native**: Fully extensible as a Python library.

## Quickstart

```bash
# Install the CLI
pip install dooma

# Initialize a new workspace
mkdir my-dsa-journey && cd my-dsa-journey
dooma init

# Start a company preparation campaign
dooma prep start Google

# Test a solution
dooma test active/two_sum/solution.py
```

## Contributing

We welcome contributions! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to get started, our architectural guidelines, and the pull request process.

Please note that this project is released with a [Contributor Code of Conduct](CODE_OF_CONDUCT.md). By participating in this project you agree to abide by its terms.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
