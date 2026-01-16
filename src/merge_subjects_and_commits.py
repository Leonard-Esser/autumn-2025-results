import pandas as pd


def merge_subjects_and_commits(
    *,
    subjects: pd.DataFrame,
    commits: pd.DataFrame,
) -> pd.DataFrame:
    merged_df = subjects.merge(
        commits,
        left_on=["full_name_of_repo", "commit_sha"],
        right_on=["full_name_of_repo", "sha"],
        how="left",
    )
    merged_df.drop(columns=["sha"])
    return merged_df
