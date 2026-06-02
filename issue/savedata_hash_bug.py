import re
import tempfile
from pathlib import Path

import pandas as pd

from SaveData_snapshot import SaveData


def extract_hash(log_path):
    log_text = Path(log_path).read_text()
    match = re.search(r"^MD5 hash: ([0-9a-f]+)$", log_text, flags=re.MULTILINE)
    if match is None:
        raise ValueError(f"Could not find MD5 hash in {log_path}.")
    return match.group(1)


def save_and_collect(df, keys, csv_path, log_path):
    SaveData(df.copy(), keys, csv_path, log_path, sortbykey=True)
    return extract_hash(log_path), Path(csv_path).read_text()


def run_case(case_name, left_df, right_df, keys):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        left_hash, left_csv = save_and_collect(
            left_df, keys, tmpdir / f"{case_name}_left.csv", tmpdir / f"{case_name}_left.log"
        )
        right_hash, right_csv = save_and_collect(
            right_df,
            keys,
            tmpdir / f"{case_name}_right.csv",
            tmpdir / f"{case_name}_right.log",
        )

    hashes_differ = left_hash != right_hash
    csv_matches = left_csv == right_csv

    print(f"Case: {case_name}")
    print(f"  left hash:  {left_hash}")
    print(f"  right hash: {right_hash}")
    print(f"  hashes differ: {hashes_differ}")
    print(f"  saved CSV identical: {csv_matches}")
    print()

    assert hashes_differ, f"{case_name}: expected different hashes from SaveData logs."
    assert csv_matches, f"{case_name}: expected identical saved CSV output."


def main():
    base = pd.DataFrame(
        {
            "id": [1, 2, 3],
            "value": [10, 20, 30],
            "label": ["a", "b", "c"],
        }
    )

    row_order_left = base.copy()
    row_order_right = base.iloc[[2, 0, 1]].copy()

    index_only_left = base.copy()
    index_only_right = base.copy()
    index_only_right.index = [10, 20, 30]

    run_case("row_order", row_order_left, row_order_right, ["id"])
    run_case("index_only", index_only_left, index_only_right, ["id"])

    print("All repro cases passed: SaveData logged different hashes for identical saved CSV output.")


if __name__ == "__main__":
    main()
