"""Build the packaged runtime index from canonical YAML data.

The YAML files under dooma/data remain the source of truth. This script creates
dooma/data/index.json, which the CLI loads at runtime to avoid parsing thousands
of YAML files on every launch.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from dooma.loader import (  # noqa: E402
    build_prebuilt_index_payload,
    serialize_prebuilt_index_payload,
)


def main() -> int:
    parser = argparse.ArgumentParser(description="Build Dooma's prebuilt runtime index.")
    parser.add_argument(
        "--data-dir",
        type=Path,
        default=ROOT / "dooma" / "data",
        help="Directory containing canonical YAML dataset folders.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "dooma" / "data" / "index.json",
        help="Path to write the generated compact JSON index.",
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit non-zero if the generated index differs from the existing file.",
    )
    args = parser.parse_args()

    payload = build_prebuilt_index_payload(data_dir=args.data_dir)
    serialized = serialize_prebuilt_index_payload(payload)

    if args.check:
        current = args.output.read_text(encoding="utf-8") if args.output.exists() else ""
        if current != serialized:
            print(f"{args.output} is stale. Run `python scripts/build_index.py`.")
            return 1
        print(f"{args.output} is current.")
        return 0

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(serialized, encoding="utf-8")
    counts = payload["counts"]
    print(
        "Built "
        f"{args.output} "
        f"({counts['questions']} questions, "
        f"{counts['companies']} companies, "
        f"{counts['company_question_mappings']} mappings)."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
