import os
import re
from pathlib import Path
from github import Github

GITHUB_TOKEN = os.environ["GITHUB_TOKEN"]
REPO_NAME = os.environ["REPO"]
PR_NUMBER = int(os.environ["PR_NUMBER"])
PR_AUTHOR = os.environ["PR_AUTHOR"]
BRANCH_NAME = os.environ["BRANCH_NAME"]
LAST_COMMIT_SHA = os.environ["LAST_COMMIT_SHA"]

ISSUE_TEMPLATE = Path(".github/post_template_issue_thread_pr_close.md")
PR_TEMPLATE = Path(".github/post_template_pr_thread_pr_close.md")


def Main():
    repo = Github(GITHUB_TOKEN).get_repo(REPO_NAME)
    pr = repo.get_pull(PR_NUMBER)

    issue_comment_url = PostIssueComment(repo)
    PostPrComment(pr, issue_comment_url)


def PostIssueComment(repo):
    issue_match = re.match(r"^(\d+)", BRANCH_NAME)
    if not issue_match:
        return None

    issue_number = int(issue_match.group(1))
    issue_body = ISSUE_TEMPLATE.read_text() + f"\n\nLast commit in issue branch: {LAST_COMMIT_SHA}"

    comment = repo.get_issue(issue_number).create_comment(issue_body)
    return comment.html_url


def PostPrComment(pr, issue_comment_url):
    pr_body = PR_TEMPLATE.read_text()

    if issue_comment_url:
        pr_body = f"[Issue summary]({issue_comment_url})\n\n{pr_body}"

    pr.as_issue().create_comment(f"@{PR_AUTHOR} {pr_body}")


if __name__ == "__main__":
    Main()
