#!/usr/bin/env python3
import sys
from pathlib import Path

TARGET = "terminated because of errors."

def Main():
    bad = []
    for p in Path(".").rglob("**/*.log"):
        try:
            if TARGET in p.read_text(errors="replace"):
                bad.append(p)
        except Exception:
            pass

    if not bad:
        print("No log files contain the error string.")
        return 0

    print("Problematic log files:")
    for p in bad:
        print(" -", p)

    return 1

if __name__ == "__main__":
    sys.exit(Main())
