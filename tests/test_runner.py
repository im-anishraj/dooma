import json
from pathlib import Path

from dooma.runner.executor import TestRunner


def test_runner_success(tmp_path: Path):
    problem_dir = tmp_path / "two_sum"
    problem_dir.mkdir()

    # Create solution.py
    (problem_dir / "solution.py").write_text(
        """
def two_sum(nums, target):
    seen = {}
    for i, num in enumerate(nums):
        diff = target - num
        if diff in seen:
            return [seen[diff], i]
        seen[num] = i
    return []
""",
        encoding="utf-8",
    )

    # Create .tests.json
    (problem_dir / ".tests.json").write_text(
        json.dumps(
            [{"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]}]
        ),
        encoding="utf-8",
    )

    success, msg = TestRunner.run_tests(problem_dir)
    assert success is True
    assert "All 1 tests passed!" in msg


def test_runner_failure(tmp_path: Path):
    problem_dir = tmp_path / "two_sum"
    problem_dir.mkdir()

    (problem_dir / "solution.py").write_text(
        """
def two_sum(nums, target):
    return [0, 0] # Wrong
""",
        encoding="utf-8",
    )

    (problem_dir / ".tests.json").write_text(
        json.dumps(
            [{"input": {"nums": [2, 7, 11, 15], "target": 9}, "expected": [0, 1]}]
        ),
        encoding="utf-8",
    )

    success, msg = TestRunner.run_tests(problem_dir)
    assert success is False
    assert "Test 1 Failed" in msg
