import json
import importlib.resources as pkg_resources
from typing import List, Dict, Any


class DatasetLoader:
    """Loads the packaged internal dataset."""

    @staticmethod
    def fetch_catalog() -> List[Dict[str, Any]]:
        """Reads the packaged catalog.json."""
        # Using importlib.resources to access packaged data
        with pkg_resources.files("dooma.dataset").joinpath("catalog.json").open("r") as f:
            return json.load(f)

    @staticmethod
    def fetch_problem(problem_id: str) -> Dict[str, Any]:
        """Reads a specific problem JSON from the package."""
        with pkg_resources.files("dooma.dataset.problems").joinpath(f"{problem_id}.json").open("r") as f:
            return json.load(f)
