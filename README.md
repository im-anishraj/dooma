<div align="center">

<br>

<h1>⚡ Dooma</h1>

**An offline-first, terminal-based Data Structures & Algorithms (DSA) practice ecosystem.**

<br>

Instead of a messy folder of random `.py` or `.cpp` files, Dooma creates a **structured, local-first workspace**. It acts as a hybrid between a package manager (pulling questions), a test runner (verifying solutions), and a progress tracker (monitoring stats and company-wise readiness).

<br>

<a href="https://pypi.org/project/dooma/"><img src="https://img.shields.io/pypi/v/dooma?style=flat-square&logo=pypi&logoColor=white&labelColor=0d1117&color=3572A5" alt="PyPI"></a>&nbsp;
<a href="https://pypi.org/project/dooma/"><img src="https://img.shields.io/pypi/pyversions/dooma?style=flat-square&logo=python&logoColor=white&labelColor=0d1117&color=3572A5" alt="Python"></a>&nbsp;
<a href="LICENSE"><img src="https://img.shields.io/badge/license-MIT-blue?style=flat-square&labelColor=0d1117" alt="MIT"></a>&nbsp;
<a href="https://gssoc.girlscript.tech/"><img src="https://img.shields.io/badge/GSSoC-2026-ff6b35?style=flat-square&labelColor=0d1117" alt="GSSoC 2026"></a>

<br><br>

```bash
pip install dooma
```

<br>

<a href="#-quickstart">Quickstart</a>&ensp;·&ensp;<a href="#-core-features">Features</a>&ensp;·&ensp;<a href="#%EF%B8%8F-how-it-works">Architecture</a>&ensp;·&ensp;<a href="#-contributing">Contribute</a>

</div>

<br>

---

<br>

## 🚀 Quickstart

Initialize your journey and start tracking your DSA progress entirely from the terminal.

```bash
# 1. Initialize a new local workspace
mkdir my-dsa-journey && cd my-dsa-journey
dooma init

# 2. Start a targeted company campaign
dooma prep start Google

# 3. Pull a problem and write your solution
# (Dooma fetches the boilerplate and metadata automatically)

# 4. Test your solution locally
dooma test active/two_sum/solution.py
```

<br>

---

<br>

## 🎯 Core Features

<table>
  <tr>
    <td width="50%" valign="top">
      <h3>💻 CLI-First Experience</h3>
      <p>Native, fast, and terminal-friendly operations built with <a href="https://github.com/Textualize/rich">Rich</a>. Experience premium UI directly in your console with color-coded test runners and progress bars.</p>
    </td>
    <td width="50%" valign="top">
      <h3>📡 Offline-First</h3>
      <p>No internet required after initial setup. All your progress, attempts, and metadata are stored locally in a high-performance SQLite database.</p>
    </td>
  </tr>
  <tr>
    <td width="50%" valign="top">
      <h3>🏢 Company Campaigns</h3>
      <p>Prepare for specific companies (e.g., Google, Amazon). Dooma curates questions and uses smart algorithms to track your readiness for technical interviews.</p>
    </td>
    <td width="50%" valign="top">
      <h3>🤖 Automated Workflows</h3>
      <p>Write your solution and let Dooma handle the rest. It automatically runs tests and moves verified solutions to a structured <code>solved/</code> archive.</p>
    </td>
  </tr>
</table>

<br>

---

<br>

## 🏗️ How It Works (Under the Hood)

Dooma isn't just a script; it's a metadata-first ecosystem. 

When you run `dooma init`, it scaffolds a structured directory and spins up a local **SQLite** database (`.dooma/metadata.db`). 

```text
my-dsa-journey/
├── .dooma/               # Internal state & SQLite DB
├── active/               # Problems you are currently working on
│   └── two_sum/
│       ├── solution.py   # Your code
│       └── tests.py      # Auto-generated tests
└── solved/               # Successfully passed algorithms
```

Every test run, success, or failure is logged. This allows Dooma to generate analytics on your success rate, weak data structures, and campaign progress without ever sending your data to a remote server.

<br>

---

<br>

## 🤝 Contributing

Dooma is participating in **[GSSoC 2026](https://gssoc.girlscript.tech/)**! We are actively looking for contributors to add more data structures, testing algorithms, and UI improvements.

### Getting Started

```bash
# Clone the repository
git clone https://github.com/im-anishraj/dooma.git
cd dooma

# Install in development mode
pip install -e ".[dev]"
```

Please review our [CONTRIBUTING.md](CONTRIBUTING.md) for architectural guidelines and the pull request process. We enforce a strict [Code of Conduct](CODE_OF_CONDUCT.md) to ensure a welcoming environment for all developers.

<br>

---

<br>

<div align="center">

<br>

**Master algorithms, not file management.**

<br>

<a href="https://pypi.org/project/dooma/"><img src="https://img.shields.io/pypi/dm/dooma?style=flat-square&logo=pypi&logoColor=white&labelColor=0d1117&color=3572A5&label=installs" alt="Downloads"></a>&ensp;
<a href="https://github.com/im-anishraj/dooma/stargazers"><img src="https://img.shields.io/github/stars/im-anishraj/dooma?style=flat-square&logo=github&labelColor=0d1117&color=e3b341&label=stars" alt="Stars"></a>&ensp;
<a href="https://github.com/im-anishraj/dooma/network/members"><img src="https://img.shields.io/github/forks/im-anishraj/dooma?style=flat-square&logo=github&labelColor=0d1117&color=8b949e&label=forks" alt="Forks"></a>

<br>

<sub>Built with Python · Licensed under MIT · Maintained by <a href="https://github.com/im-anishraj">@im-anishraj</a></sub>

</div>
