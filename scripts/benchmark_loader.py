"""Benchmark Dooma index loading paths."""

from __future__ import annotations

import argparse
import statistics
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dooma.loader import _DATA_DIR, load_index  # noqa: E402


def _measure(label: str, runs: int, load_func) -> None:
    timings: list[float] = []
    questions = 0

    for _ in range(runs):
        start = time.perf_counter()
        index = load_func()
        timings.append(time.perf_counter() - start)
        questions = len(index.questions)

    print(
        f"{label}: "
        f"min={min(timings):.3f}s "
        f"median={statistics.median(timings):.3f}s "
        f"max={max(timings):.3f}s "
        f"runs={runs} "
        f"questions={questions}"
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark Dooma index startup cost.")
    parser.add_argument("--runs", type=int, default=3, help="Number of cold loads per path.")
    parser.add_argument(
        "--fast-only",
        action="store_true",
        help="Only benchmark the packaged prebuilt index path.",
    )
    args = parser.parse_args()

    if args.runs < 1:
        parser.error("--runs must be at least 1")

    _measure("prebuilt index.json", args.runs, lambda: load_index(force=True))
    if not args.fast_only:
        _measure(
            "YAML fallback",
            args.runs,
            lambda: load_index(data_dir=_DATA_DIR, force=True),
        )

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
