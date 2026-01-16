import argparse
from pathlib import Path

import pandas as pd

import config
from data_access import commits, data, subjects
from domain_model import Subject
from draw_k_random_subjects import draw_k_random_subjects
from export import export_df, export_subjects
from merge_subjects_and_commits import merge_subjects_and_commits


def _build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser()
    p.add_argument(
        "--prepare-manual-verification",
        action="store_true",
        help="TODO",
    )
    return p


def _prepare_manual_verification(
    *,
    root: Path,
    manual_verification_scope: int | None = None,
    random_state: int | None = None,
):
    k = manual_verification_scope
    k_random_subjects: set[Subject] = draw_k_random_subjects(
        subjects(root),
        k=k,
        random_state=random_state,
    )
    export_subjects(
        k_random_subjects,
        path=data(root) / f"{k}_random_subjects.csv",
        subjects_are_actually_bare_results=False,
    )
    path = export_subjects(
        k_random_subjects,
        path=data(root) / f"{k}_random_bare_results.csv",
        subjects_are_actually_bare_results=True,
    )
    subjects_df = pd.read_csv(path)
    df = merge_subjects_and_commits(
        subjects=subjects_df,
        commits=pd.read_csv(commits(root)),
    )
    export_df(
        df[config.COLUMNS_FOR_MANUAL_VERIFICATION],
        path=data(root) / f"manual_verification_of_{k}_random_subjects.csv",
    )


def main():
    root = Path(__file__).resolve().parent.parent
    args = _build_parser().parse_args()
    if args.prepare_manual_verification:
        _prepare_manual_verification(
            root=root,
            manual_verification_scope=config.MANUAL_VERIFICATION_SCOPE,
            random_state=config.RANDOM_STATE,
        )


if __name__ == "__main__":
    main()
