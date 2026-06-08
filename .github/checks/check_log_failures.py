#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

RUN_CSV = Path("output") / "run.csv"

def Main():
    with open(RUN_CSV, newline="") as f:
        rows = list(csv.DictReader(f))

    failed = [row for row in rows if row["success"] != "1"]
    if not failed:
        print("All builds succeeded.")
        return 0

    print("Failed scripts:")
    for row in failed:
        print(" -", row["filename"])

    return 1

if __name__ == "__main__":
    sys.exit(Main())
