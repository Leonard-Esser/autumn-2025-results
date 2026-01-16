import csv
import random
from pathlib import Path

from domain_model import Subject


def draw_k_random_subjects(
    path: Path,
    *,
    k: int | None = None,
    random_state: int | None = None,
) -> set[Subject]:
    subjects: set[Subject] = set()
    with path.open("r", newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            subjects.add(
                Subject(
                    full_name_of_repo=row["full_name_of_repo"],
                    commit_sha=row["commit_sha"],
                    path=row["path"],
                )
            )
    if k is not None and 0 < k < len(subjects):
        if random_state is not None:
            random.seed(random_state)
        subjects = set(random.sample(list(subjects), k))
    return subjects
