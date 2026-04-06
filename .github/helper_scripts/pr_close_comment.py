import os
import re
import sys
from pathlib import Path
from github import Github

ISSUE_TEMPLATE = Path(".github/post_template_issue_thread_pr_close.md")
PR_TEMPLATE = Path(".github/post_template_pr_thread_pr_close.md")


def Main():
    github_token    = os.environ["GITHUB_TOKEN"]
    repo_name       = os.environ["REPO"]
    pr_number       = int(os.environ["PR_NUMBER"])
    user_closing_pr = os.environ["USER_CLOSING_PR"]
    branch_name     = os.environ["BRANCH_NAME"]
    last_commit_sha = os.environ["LAST_COMMIT_SHA"]

    repo = Github(github_token).get_repo(repo_name)
    pr = repo.get_pull(pr_number)

    merge_commit_sha  = pr.merge_commit_sha
    issue_comment_url = PostCommentOnIssueThread(repo, branch_name, last_commit_sha, merge_commit_sha)
    PostCommentOnPRThread(pr, user_closing_pr, issue_comment_url)
    return 0


def PostCommentOnIssueThread(repo, branch_name, last_commit_sha, merge_commit_sha):
    issue_match = re.match(r"^(\d+)", branch_name)
    if not issue_match:
        return None

    issue_number = int(issue_match.group(1))
    issue_body   = ISSUE_TEMPLATE.read_text()
    issue_body  += f"\n\nLast commit in issue branch: {last_commit_sha}"
    if merge_commit_sha:
        issue_body += f"\n\nMerge commit: {merge_commit_sha}"

    comment = repo.get_issue(issue_number).create_comment(issue_body)
    return comment.html_url


def PostCommentOnPRThread(pr, user_closing_pr, issue_comment_url):
    post_content = PR_TEMPLATE.read_text()

    if issue_comment_url:
        post_content = f"[Issue summary]({issue_comment_url})\n\n{post_content}"

    pr.as_issue().create_comment(f"@{user_closing_pr} {post_content}")


if __name__ == "__main__":
    sys.exit(Main())
