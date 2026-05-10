from pathlib import Path

# Mock developer script to show how we would scrape upstream repos
# and build the internal dooma/dataset directory before releasing a package.


def build():
    # In a real scenario, this would `requests.get` the open source GitHub repository,
    # parse the READMEs, extract constraints, compile tests, and dump to JSON.
    print("Building Dooma offline dataset from upstream sources...")

    # Dump paths
    cwd = Path(__file__).parent.parent
    dataset_dir = cwd / "dooma" / "dataset"
    problems_dir = dataset_dir / "problems"

    # ... logic already executed via manual JSON generation ...
    print(f"Built {len(list(problems_dir.glob('*.json')))} problems into {dataset_dir}")


if __name__ == "__main__":
    build()
