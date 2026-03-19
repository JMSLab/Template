import os
import re
from pathlib import Path
from github import Github

ISSUE_TEMPLATE = Path(".github/post_template_issue_thread_pr_close.md")
PR_TEMPLATE = Path(".github/post_template_pr_thread_pr_close.md")


def Main():
    github_token    = os.environ["GITHUB_TOKEN"]
    repo_name       = os.environ["REPO"]
    pr_number       = int(os.environ["PR_NUMBER"])
    pr_author       = os.environ["PR_AUTHOR"]
    branch_name     = os.environ["BRANCH_NAME"]
    last_commit_sha = os.environ["LAST_COMMIT_SHA"]

    repo = Github(github_token).get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    issue_comment_url = PostIssueComment(repo, branch_name, last_commit_sha)
    PostPrComment(pr, pr_author, issue_comment_url)


def PostIssueComment(repo, branch_name, last_commit_sha):
    issue_match = re.match(r"^(\d+)", branch_name)
    if not issue_match:
        return None

    issue_number = int(issue_match.group(1))
    issue_body = ISSUE_TEMPLATE.read_text() + f"\n\nLast commit in issue branch: {last_commit_sha}"

    comment = repo.get_issue(issue_number).create_comment(issue_body)
    return comment.html_url


def PostPrComment(pr, pr_author, issue_comment_url):
    pr_body = PR_TEMPLATE.read_text()

    if issue_comment_url:
        pr_body = f"[Issue summary]({issue_comment_url})\n\n{pr_body}"

    pr.as_issue().create_comment(f"@{pr_author} {pr_body}")


if __name__ == "__main__":
    Main()
