import csv
from collections.abc import Iterable
from operator import itemgetter
from pathlib import Path

import pandas as pd

from domain_model import Subject


def export_subjects(
    subjects: Iterable[Subject],
    *,
    path: Path,
    subjects_are_actually_bare_results: bool,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    sort_key = itemgetter(0, 1, 2)
    if subjects_are_actually_bare_results:
        header = [
            "full_name_of_repo",
            "commit_sha",
            "path",
            "is_ccdc_event",
            "detected_channel",
        ]
        rows = {(s.full_name_of_repo, s.commit_sha, s.path, False, None) for s in subjects}
    else:
        header = ["full_name_of_repo", "commit_sha", "path"]
        rows = {(s.full_name_of_repo, s.commit_sha, s.path) for s in subjects}
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(header)
        writer.writerows(sorted(rows, key=sort_key))
    return path


def export_df(
    df: pd.DataFrame,
    *,
    path: Path,
    index: bool = False,
) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=index)
    return path
