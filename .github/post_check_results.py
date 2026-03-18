#!/usr/bin/env python3
import os
import subprocess
import sys

CHECKS = [
    ("SCons DAG", "check_scons"),
    ("Newlines",  "check_newlines"),
    ("EPS data",  "check_eps"),
    ("Build log", "check_scons_log"),
]

def Main():
    repo   = os.environ["GITHUB_REPOSITORY"]
    run_id = os.environ["GITHUB_RUN_ID"]

    print("Runtime:")
    rows, failed = CollectResults()

    if "--post" in sys.argv:
        PostResults(repo, run_id, rows, failed)

    if failed:
        print(f"Failed checks: {', '.join(failed)}")
        return 1
    return 0

def CollectResults():
    rows, failed = [], []
    for name, step_id in CHECKS:
        key     = step_id.upper()
        outcome = os.environ.get(f"{key}_OUTCOME", "skipped")
        time    = os.environ.get(f"{key}_TIME", "")
        print(f"  {step_id}: {time}s")
        if outcome == "skipped":
            rows.append(f"| {name} | SKIP | |")
        elif outcome == "success":
            rows.append(f"| {name} | ✅ | {time}s |")
        else:
            failed.append(name)
            rows.append(f"| {name} | ❌ | {time}s |")
    return rows, failed

def PostResults(repo, run_id, rows, failed):
    run_url    = f"https://github.com/{repo}/actions/runs/{run_id}"
    table      = "\n".join(["| Check | Result | Time |", "|-------|--------|------|", *rows])
    body       = f"**Check Results** ([run details]({run_url}))\n\n{table}"
    pr_num     = os.environ["PR_NUMBER"]
    pr_sha     = os.environ["PR_SHA"]
    subprocess.run([
        "gh", "api", f"repos/{repo}/issues/{pr_num}/comments",
        "--method", "POST", "-f", f"body={body}",
    ], check=True)
    state = "failure" if failed else "success"
    desc  = f"Failed: {', '.join(failed)}" if failed else "All checks passed"
    subprocess.run([
        "gh", "api", f"repos/{repo}/statuses/{pr_sha}",
        "-f", f"state={state}", "-f", "context=Checks",
        "-f", f"description={desc}", "-f", f"target_url={run_url}",
    ], check=True)

if __name__ == "__main__":
    sys.exit(Main())
