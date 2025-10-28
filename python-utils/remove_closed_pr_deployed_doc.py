from __future__ import annotations

from typing import TYPE_CHECKING
import os
import shutil
from pathlib import Path

from github import Github, Auth, UnknownObjectException

if TYPE_CHECKING:
    from github.Repository import Repository
    from github.PullRequest import PullRequest
    from github.ContentFile import ContentFile

PR_COMMENT = "This PR has been closed. Documentation for this pull request will shortly be removed from its "\
             "[former deployment address](https://{cname}/pull/{pr_number})."

def get_token_from_environment() -> str:
    """Return the github access token.

    This token should have org:read, enterprise:read, and repo:full

    """
    access_token = os.environ.get("GITHUB_TOKEN", "")
    if not access_token:
        raise Exception("Missing 'GITHUB_TOKEN' environment variable")
    return access_token

def get_repo_slug_from_environment() -> str:
    repo_slug = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo_slug:
        raise Exception("Missing 'GITHUB_REPOSITORY' environment variable")
    return repo_slug

def get_deployment_branch_name_from_environment() -> str:
    branch = os.environ.get("BRANCH", "")
    if not branch:
        raise Exception("Missing 'BRANCH' environment variable")
    return branch

def get_documentation_cname_from_environment() -> str:
    cname = os.environ.get("CNAME", "")
    if not cname:
        raise Exception("Missing 'CNAME' environment variable")
    return cname

def get_deployed_prs_contents(repo: Repository, branch: str) -> list[ContentFile]:
    try:
        deployed_pr_docs = repo.get_contents(path="pull", ref=branch)
        return deployed_pr_docs
    except UnknownObjectException: # means pull/ is not present
        return []
    
def get_opened_prs(repo: Repository) -> list[PullRequest]:
    repo_prs = repo.get_pulls(state="opened")
    return list(repo_prs)

def deployed_pr_numbers(content_list: list[ContentFile]) -> list[str]:
    return [content.path.removeprefix("pull/") for content in content_list]

def opened_pr_numbers(pr_list: list[PullRequest]) -> list[str]:
    return [str(pr.number) for pr in pr_list]

def prs_to_remove(deployed_prs: list[str], open_prs: list[str]) -> list[str]:
    closed_prs_with_deployed_doc = list(set(deployed_prs) - set(open_prs))
    return closed_prs_with_deployed_doc

def remove_prs_doc(prs_to_remove: list[str]):
    pull_path = Path("pull")
    for pr in prs_to_remove:
        shutil.rmtree(pull_path / pr)
    if len(os.listdir(pull_path)) == 0:
        pull_path.rmdir()

def add_comment_to_closed_prs(repo: Repository, cname: str, removed_prs: list[str]):
    for pr_number in removed_prs:
        issue = repo.get_issue(number=int(pr_number))
        issue.create_comment(PR_COMMENT.format(cname=cname, pr_number=pr_number))

if __name__ == "__main__":
    auth_string = get_token_from_environment()
    repo_slug = get_repo_slug_from_environment()
    branch = get_deployment_branch_name_from_environment()
    cname = get_documentation_cname_from_environment()
    auth = Auth.Token(auth_string)
    gh = Github(auth=auth)
    repo = gh.get_repo(repo_slug)

    deployed_pr_contents = get_deployed_prs_contents(repo, branch)
    opened_prs = get_opened_prs(repo)
    deployed_pr_nums = deployed_pr_numbers(deployed_pr_contents)
    opened_pr_nums = opened_pr_numbers(opened_prs)
    prs_remove_list = prs_to_remove(deployed_pr_nums, opened_pr_nums)

    if prs_remove_list:
        remove_prs_doc(prs_remove_list)
        add_comment_to_closed_prs(repo, cname, prs_remove_list)
    
    # remove_prs_doc(repo, deployed_pr_contents, prs_remove_list)

# TODO: The repo slug should be fetched dynamically
#       The auth_string should be secrets.GITHUB_TOKEN
#       The documentation deployment branch should be dynamic, it is not necessarily gh-pages