#!/usr/bin/env python3
import csv
import sys
from pathlib import Path

RUN_CSV = Path("output") / "run.csv"

def Main():
    with open(RUN_CSV, newline="") as f:
        rows = list(csv.DictReader(f))

    script_failed = [row for row in rows if row["success"] != "1"]
    
    sconstruct = Path("sconstruct.log").read_text()
    scons_failed = (
        "done building targets." not in sconstruct
        or "errors occurred during build" in sconstruct
        or "building terminated because of errors" in sconstruct
    )

    if not script_failed and not scons_failed:
        print("All builds succeeded.")
        return 0

    print("Failed scripts:")
    for row in script_failed:
        print(" -", row["filename"])
    if scons_failed:
        print("SCons build failed. Check sconstruct.log for details.")
    return 1

if __name__ == "__main__":
    sys.exit(Main())
