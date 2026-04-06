#!/usr/bin/env python3
import subprocess
import sys


def Main():
    files = subprocess.run(
        ["git", "ls-files", "issue/"],
        stdout=subprocess.PIPE, check=True
    ).stdout.decode().splitlines()

    if files:
        print("This pull includes an issue subdirectory. Please remove prior to merging.")
        for f in files:
            print(" -", f)
        return 1

    print("No issue/ files found.")
    return 0


if __name__ == "__main__":
    sys.exit(Main())
