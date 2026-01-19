import csv
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path

from data_access import output, raw_results, truth


@dataclass(frozen=True, slots=True)
class _Agg:
    """Aggregated view per subject-key (one subject may have multiple rows due to channels)."""

    is_ccdc_event: bool
    channels: frozenset[str]


def _verify(
    *,
    expected: Path,
    actual: Path,
    report: Path,
    reports_on_extra_subjects: bool = False,
) -> None:
    key_cols = ("full_name_of_repo", "commit_sha", "path")

    def _norm(s: str | None) -> str:
        return (s or "").strip()

    def _parse_bool(s: str | None) -> bool:
        v = _norm(s).lower()
        if v in {"true", "1", "yes", "y", "t"}:
            return True
        if v in {"false", "0", "no", "n", "f", ""}:
            return False
        raise ValueError(f"Invalid boolean value for is_ccdc_event: {s!r}")

    def _read_agg(p: Path) -> dict[tuple[str, str, str], _Agg]:
        per_key_is: dict[tuple[str, str, str], bool] = {}
        per_key_channels: dict[tuple[str, str, str], set[str]] = defaultdict(set)

        with p.open("r", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            if reader.fieldnames is None:
                raise ValueError(f"{p} has no header row")

            missing = [
                c
                for c in (*key_cols, "is_ccdc_event", "detected_channel")
                if c not in reader.fieldnames
            ]
            if missing:
                raise ValueError(
                    f"{p} is missing required columns: {missing}. Found: {reader.fieldnames}"
                )

            for row in reader:
                key = tuple(_norm(row[c]) for c in key_cols)  # type: ignore[misc]
                is_ev = _parse_bool(row.get("is_ccdc_event"))
                ch = _norm(row.get("detected_channel"))

                if key in per_key_is and per_key_is[key] != is_ev:
                    raise ValueError(
                        f"Inconsistent is_ccdc_event for same subject key in {p}: "
                        f"key={key} had {per_key_is[key]} then {is_ev}"
                    )
                per_key_is[key] = is_ev
                if ch:
                    per_key_channels[key].add(ch)

        return {
            k: _Agg(is_ccdc_event=per_key_is[k], channels=frozenset(per_key_channels[k]))
            for k in per_key_is
        }

    exp = _read_agg(expected)
    act = _read_agg(actual)

    exp_keys = set(exp)
    act_keys = set(act)

    missing_in_actual = sorted(exp_keys - act_keys)
    extra_in_actual = sorted(act_keys - exp_keys)

    # Compare only for subjects present in expected (as requested)
    tp = tn = fp = fn = 0
    channel_ok = channel_mismatch = 0
    mismatches: list[tuple[tuple[str, str, str], bool, bool]] = []
    channel_mismatches: list[tuple[tuple[str, str, str], frozenset[str], frozenset[str]]] = []

    for key in sorted(exp_keys & act_keys):
        e = exp[key]
        a = act[key]

        if e.is_ccdc_event and a.is_ccdc_event:
            tp += 1
        elif (not e.is_ccdc_event) and (not a.is_ccdc_event):
            tn += 1
        elif (not e.is_ccdc_event) and a.is_ccdc_event:
            fp += 1
        else:
            fn += 1

        if e.is_ccdc_event != a.is_ccdc_event:
            mismatches.append((key, e.is_ccdc_event, a.is_ccdc_event))

        # Only compare channels if expected says it's truly a ccdc event
        if e.is_ccdc_event:
            if e.channels == a.channels:
                channel_ok += 1
            else:
                channel_mismatch += 1
                channel_mismatches.append((key, e.channels, a.channels))

    total_compared = len(exp_keys & act_keys)

    def _fmt_key(k: tuple[str, str, str]) -> str:
        full_name, sha, path = k
        return f"{full_name} | {sha} | {path}"

    report.parent.mkdir(parents=True, exist_ok=True)
    with report.open("w", encoding="utf-8") as out:
        out.write("Verification report\n")
        out.write("===================\n\n")

        out.write(f"Expected file: {expected}\n")
        out.write(f"Actual file:   {actual}\n\n")

        out.write("Subject key columns: full_name_of_repo, commit_sha, path\n")
        out.write("Note: Channels are compared ONLY when expected.is_ccdc_event == True.\n\n")

        out.write("Coverage\n")
        out.write("--------\n")
        out.write(f"Subjects in expected: {len(exp_keys)}\n")
        out.write(f"Subjects in actual:   {len(act_keys)}\n")
        out.write(f"Subjects compared (intersection): {total_compared}\n")
        out.write(f"Missing in actual (expected - actual): {len(missing_in_actual)}\n")
        out.write(f"Extra in actual (actual - expected):   {len(extra_in_actual)}\n\n")

        out.write("Classification (based on is_ccdc_event)\n")
        out.write("--------------------------------------\n")
        out.write(f"TP: {tp}\n")
        out.write(f"TN: {tn}\n")
        out.write(f"FP: {fp}\n")
        out.write(f"FN: {fn}\n\n")

        out.write("Channel comparison (only where expected.is_ccdc_event == True)\n")
        out.write("-------------------------------------------------------------\n")
        out.write(f"Channel OK:        {channel_ok}\n")
        out.write(f"Channel mismatches:{channel_mismatch}\n\n")

        if missing_in_actual:
            out.write("Missing subjects in actual\n")
            out.write("--------------------------\n")
            for k in missing_in_actual:
                out.write(f"- {_fmt_key(k)}\n")
            out.write("\n")

        if extra_in_actual and reports_on_extra_subjects:
            out.write("Extra subjects in actual\n")
            out.write("------------------------\n")
            for k in extra_in_actual:
                out.write(f"- {_fmt_key(k)}\n")
            out.write("\n")

        if mismatches:
            out.write("is_ccdc_event mismatches\n")
            out.write("------------------------\n")
            for k, e_is, a_is in mismatches:
                out.write(f"- {_fmt_key(k)} | expected={e_is} actual={a_is}\n")
            out.write("\n")

        if channel_mismatches:
            out.write("Channel mismatches (expected.is_ccdc_event == True)\n")
            out.write("--------------------------------------------------\n")
            for k, e_ch, a_ch in channel_mismatches:
                out.write(f"- {_fmt_key(k)}\n")
                out.write(f"  expected_channels={sorted(e_ch)}\n")
                out.write(f"  actual_channels  ={sorted(a_ch)}\n")
            out.write("\n")


def main():
    root = Path(__file__).resolve().parent.parent
    _verify(expected=truth(root), actual=raw_results(root), report=output(root) / "verified.txt")


if __name__ == "__main__":
    main()
