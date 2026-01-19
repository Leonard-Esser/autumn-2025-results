import csv
from pathlib import Path

from data_access import raw_results


def _verify_each_row_has_the_same_set_of_columns(
    *,
    path: Path,
) -> None:
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        rows = list(reader)

    expected_cols = len(rows[0])

    bad_rows = [(i, len(r)) for i, r in enumerate(rows) if len(r) != expected_cols]

    print("Bad rows:", bad_rows[:10])


def main():
    root = Path(__file__).resolve().parent.parent
    _verify_each_row_has_the_same_set_of_columns(
        path=raw_results(root),
    )


if __name__ == "__main__":
    main()
