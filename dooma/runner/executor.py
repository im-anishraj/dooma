import importlib.util
import json
import sys
import time
from pathlib import Path
from typing import Tuple


class TestRunner:
    """Executes a user's Python solution against a set of test cases."""

    @staticmethod
    def run_tests(problem_dir: Path) -> Tuple[bool, str]:
        """
        Runs tests for the given problem directory.
        Returns a tuple: (Success: bool, Message: str)
        """
        solution_path = problem_dir / "solution.py"
        tests_path = problem_dir / ".tests.json"

        if not solution_path.exists():
            return False, f"File not found: {solution_path}"
        if not tests_path.exists():
            return False, f"Tests not found: {tests_path}"

        try:
            tests = json.loads(tests_path.read_text())
        except json.JSONDecodeError:
            return False, "Failed to parse .tests.json"

        # Dynamically load the user's module
        module_name = f"dooma_solution_{int(time.time())}"
        spec = importlib.util.spec_from_file_location(module_name, str(solution_path))
        if spec is None or spec.loader is None:
            return False, "Failed to load solution.py"

        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module

        try:
            spec.loader.exec_module(module)
        except Exception as e:
            return False, f"Error compiling/running solution.py:\n{e}"

        # Find the function to call. Assume it's the only non-dunder callable
        callables = [
            v
            for k, v in module.__dict__.items()
            if callable(v) and not k.startswith("_")
        ]
        if not callables:
            return False, "No function found in solution.py"

        func = callables[-1]  # Usually the last defined function is the main one

        # Execute tests
        for idx, test in enumerate(tests):
            inputs = test.get("input", {})
            expected = test.get("expected")

            try:
                # Assuming inputs is a dict of kwargs
                result = func(**inputs)
                if result != expected:
                    return (
                        False,
                        f"Test {idx + 1} Failed.\nInput: {inputs}\nExpected: {expected}\nGot: {result}",
                    )
            except Exception as e:
                return False, f"Test {idx + 1} Error.\nInput: {inputs}\nException: {e}"

        return True, f"All {len(tests)} tests passed!"
