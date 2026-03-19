#!/usr/bin/env python3
import json
import os
import subprocess
import sys

CHECKS_JSON = os.path.join(os.path.dirname(__file__), '../checks/checks.json')

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
    checks      = json.load(open(CHECKS_JSON))
    results_dir = os.path.join(os.environ["RUNNER_TEMP"], "check_results")
    rows, failed = [], []
    for check in checks:
        name        = check["name"]
        result_file = os.path.join(results_dir, f"{name}.json")
        if os.path.exists(result_file):
            result  = json.load(open(result_file))
            outcome = result["outcome"]
            time    = result["time"]
            print(f"  {name}: {time}s")
            if outcome == "success":
                rows.append(f"| {name} | ✅ | {time}s |")
            else:
                failed.append(name)
                rows.append(f"| {name} | ❌ | {time}s |")
        else:
            print(f"  {name}: skipped")
            rows.append(f"| {name} | SKIP | |")
    return rows, failed

def PostResults(repo, run_id, rows, failed):
    checks  = json.load(open(CHECKS_JSON))
    run_url = f"https://github.com/{repo}/actions/runs/{run_id}"
    table   = "\n".join(["| Check | Result | Time |", "|-------|--------|------|", *rows])
    commands = " · ".join(f"`{c['command']}`" for c in checks if "command" in c) + " · `/run-actions-all`"
    body    = f"**Check Results** ([run details]({run_url}))\n\n{table}\n\nRun individually: {commands}"
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
