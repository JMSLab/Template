import importlib.util
import re
import tempfile
from pathlib import Path

import pandas as pd


def load_savedata(save_data_path, module_name):
    spec = importlib.util.spec_from_file_location(module_name, save_data_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.SaveData


OLD_SAVEDATA = load_savedata(Path(__file__).with_name("SaveData_snapshot.py"), "savedata_old")
NEW_SAVEDATA = load_savedata(
    Path(__file__).resolve().parents[1] / "source" / "lib" / "SaveData.py",
    "savedata_new",
)


def extract_hash(log_path):
    log_text = Path(log_path).read_text()
    match = re.search(r"^MD5 hash: ([0-9a-f]+)$", log_text, flags=re.MULTILINE)
    if match is None:
        raise ValueError(f"Could not find MD5 hash in {log_path}.")
    return match.group(1)


def save_and_collect(save_data, df, keys, csv_path, log_path):
    save_data(df.copy(), keys, csv_path, log_path, sortbykey=True)
    return extract_hash(log_path), Path(csv_path).read_text()


def run_case(save_data, label, case_name, left_df, right_df, keys, expect_hashes_differ):
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)
        left_hash, left_csv = save_and_collect(
            save_data,
            left_df,
            keys,
            tmpdir / f"{case_name}_left.csv",
            tmpdir / f"{case_name}_left.log",
        )
        right_hash, right_csv = save_and_collect(
            save_data,
            right_df,
            keys,
            tmpdir / f"{case_name}_right.csv",
            tmpdir / f"{case_name}_right.log",
        )

    hashes_differ = left_hash != right_hash
    csv_matches = left_csv == right_csv

    print(f"{label} | Case: {case_name}")
    print(f"  left hash:  {left_hash}")
    print(f"  right hash: {right_hash}")
    print(f"  hashes differ: {hashes_differ}")
    print(f"  saved CSV identical: {csv_matches}")
    print()

    assert hashes_differ == expect_hashes_differ, (
        f"{label} {case_name}: expected hashes_differ={expect_hashes_differ}, "
        f"got {hashes_differ}."
    )
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

    cases = [
        ("row_order", row_order_left, row_order_right, True, False),
        ("index_only", index_only_left, index_only_right, True, False),
    ]

    for case_name, left_df, right_df, old_expect, new_expect in cases:
        run_case(OLD_SAVEDATA, "old SaveData", case_name, left_df, right_df, ["id"], old_expect)
        run_case(NEW_SAVEDATA, "new SaveData", case_name, left_df, right_df, ["id"], new_expect)

    print("Comparison passed: old and new SaveData behavior matches the expected repro outcomes.")


if __name__ == "__main__":
    main()
