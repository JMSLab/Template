#!/usr/bin/env python3
import json
import os
import subprocess
import sys
from pathlib import Path

CHECKS_JSON = Path(__file__).parent.parent / 'checks' / 'checks.json'

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
    checks      = json.loads(CHECKS_JSON.read_text())
    results_dir = Path(os.environ["RUNNER_TEMP"]) / "check_results"
    rows, failed = [], []
    STATUS = {"success": "✅", "failure": "❌"}
    for check in checks:
        check_name  = check["name"]
        result_file = results_dir / f"{check_name}.json"
        if result_file.exists():
            result      = json.loads(result_file.read_text())
            outcome     = result["outcome"]
            elapsed     = result["time"]
            print(f"  {check_name}: {elapsed}s")
            status_icon = STATUS.get(outcome, "❌")
            if outcome != "success":
                failed.append(check_name)
            rows.append(f"| {check_name} | {status_icon} | {elapsed}s |")
        else:
            print(f"  {check_name}: skipped")
            rows.append(f"| {check_name} | SKIP | |")
    return rows, failed

def PostResults(repo, run_id, rows, failed):
    run_url        = f"https://github.com/{repo}/actions/runs/{run_id}"
    comment_author = os.environ.get("COMMENT_AUTHOR", "")
    comment_url    = os.environ.get("COMMENT_URL", "")
    table          = "\n".join(["| Check | Result | Time |", "|-------|--------|------|", *rows])
    attribution    = f"Triggered by @{comment_author} on [this comment]({comment_url})\n\n" if comment_author else ""
    body           = f"{attribution}**Check Results** ([run details]({run_url}))\n\n{table}"
    pr_num  = os.environ["PR_NUMBER"]
    pr_sha  = os.environ["PR_SHA"]
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
