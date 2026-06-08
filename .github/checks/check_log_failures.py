#!/usr/bin/env python3
import sys
from pathlib import Path

import pandas as pd

RUN_CSV = Path("output") / "run.csv"

def Main():
    df = pd.read_csv(RUN_CSV)

    failed = df[df['success'] != 1]
    if failed.empty:
        print("All builds succeeded.")
        return 0

    print("Failed scripts:")
    for filename in failed['filename']:
        print(" -", filename)

    return 1

if __name__ == "__main__":
    sys.exit(Main())
