from pathlib import Path


def data(root: Path) -> Path:
    return root / "data"


def output(root: Path) -> Path:
    return data(root) / "output"


def raw_results(root: Path) -> Path:
    return data(root) / "raw_results" / "raw_results.csv"


def subjects(root: Path) -> Path:
    return data(root) / "raw_results" / "subjects.csv"


def commits(root: Path) -> Path:
    return data(root) / "raw_results" / "commits.csv"


def truth(root: Path) -> Path:
    return data(root) / "truth" / "truth.csv"
