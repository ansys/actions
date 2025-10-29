from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING

from github import Auth, Github, UnknownObjectException

if TYPE_CHECKING:
    from github.ContentFile import ContentFile
    from github.PullRequest import PullRequest
    from github.Repository import Repository

PR_COMMENT = (
    "This PR has been closed. Documentation for this pull request will shortly be removed from its "
    "[former deployment address](https://{cname}/pull/{pr_number})."
)


def get_token_from_environment() -> str:
    """Return the github access token.

    This token should have org:read, enterprise:read, and repo:full permissions.

    Returns
    -------
    str
        The GitHub access token from environment variables.

    Raises
    ------
    Exception
        If GITHUB_TOKEN environment variable is not set.
    """
    access_token = os.environ.get("GITHUB_TOKEN", "")
    if not access_token:
        raise Exception("Missing 'GITHUB_TOKEN' environment variable")
    return access_token


def get_repo_slug_from_environment() -> str:
    """Get the GitHub repository slug from environment variables.

    Returns
    -------
    str
        Repository slug in format 'owner/repository'.

    Raises
    ------
    Exception
        If GITHUB_REPOSITORY environment variable is not set.
    """
    repo_slug = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo_slug:
        raise Exception("Missing 'GITHUB_REPOSITORY' environment variable")
    return repo_slug


def get_deployment_branch_name_from_environment() -> str:
    """Get the deployment branch name from environment variables.

    Returns
    -------
    str
        The branch name where documentation is deployed.

    Raises
    ------
    Exception
        If BRANCH environment variable is not set.
    """
    branch = os.environ.get("BRANCH", "")
    if not branch:
        raise Exception("Missing 'BRANCH' environment variable")
    return branch


def get_documentation_cname_from_environment() -> str:
    """Get the documentation CNAME from environment variables.

    Returns
    -------
    str
        The canonical domain name for documentation deployment.

    Raises
    ------
    Exception
        If CNAME environment variable is not set.
    """
    cname = os.environ.get("CNAME", "")
    if not cname:
        raise Exception("Missing 'CNAME' environment variable")
    return cname


def get_deployed_prs_contents(repo: Repository, branch: str) -> list[ContentFile]:
    """Get the contents of deployed PR documentation from repository.

    Parameters
    ----------
    repo : Repository
        GitHub repository object.
    branch : str
        The branch name to retrieve contents from.

    Returns
    -------
    list[ContentFile]
        List of content files in the 'pull' directory,
        or empty list if the directory doesn't exist.
    """
    try:
        deployed_pr_docs = repo.get_contents(path="pull", ref=branch)
        # Ensure we always return a list, as get_contents can return a single file or list
        if isinstance(deployed_pr_docs, list):
            return deployed_pr_docs
        else:
            return [deployed_pr_docs]
    except UnknownObjectException:  # means pull/ is not present
        return []


def get_opened_prs(repo: Repository) -> list[PullRequest]:
    """Get all opened pull requests from the repository.

    Parameters
    ----------
    repo : Repository
        GitHub repository object.

    Returns
    -------
    list[PullRequest]
        List of all opened pull request objects.
    """
    repo_prs = repo.get_pulls(state="opened")
    return list(repo_prs)


def deployed_pr_numbers(content_list: list[ContentFile]) -> list[str]:
    """Extract PR numbers from deployed documentation content files.

    Parameters
    ----------
    content_list : list[ContentFile]
        List of content files from the 'pull' directory.

    Returns
    -------
    list[str]
        List of PR numbers as strings, extracted from file paths.
    """
    return [content.path.removeprefix("pull/") for content in content_list]


def opened_pr_numbers(pr_list: list[PullRequest]) -> list[str]:
    """Extract PR numbers from opened pull request objects.

    Parameters
    ----------
    pr_list : list[PullRequest]
        List of opened pull request objects.

    Returns
    -------
    list[str]
        List of PR numbers as strings.
    """
    return [str(pr.number) for pr in pr_list]


def prs_to_remove(deployed_prs: list[str], open_prs: list[str]) -> list[str]:
    """Determine which PR documentation should be removed.

    Compares deployed PR documentation with currently opened PRs to identify
    closed PRs that still have deployed documentation.

    Parameters
    ----------
    deployed_prs : list[str]
        List of PR numbers that have deployed documentation.
    open_prs : list[str]
        List of PR numbers that are currently open.

    Returns
    -------
    list[str]
        List of PR numbers for closed PRs that have deployed
        documentation and should be removed.
    """
    closed_prs_with_deployed_doc = list(set(deployed_prs) - set(open_prs))
    return closed_prs_with_deployed_doc


def remove_prs_doc(prs_to_remove: list[str]):
    """Remove documentation directories for specified PRs.

    Removes the local documentation directories for the given PR numbers.
    If the 'pull' directory becomes empty after removal, it is also deleted.

    Parameters
    ----------
    prs_to_remove : list[str]
        List of PR numbers whose documentation should be removed.
    """
    pull_path = Path("pull")
    for pr in prs_to_remove:
        shutil.rmtree(pull_path / pr)
    if len(os.listdir(pull_path)) == 0:
        pull_path.rmdir()


def add_comment_to_closed_prs(repo: Repository, cname: str, removed_prs: list[str]):
    """Add notification comments to closed PRs about documentation removal.

    Posts a comment on each closed PR informing that the documentation
    deployment has been removed.

    Parameters
    ----------
    repo : Repository
        GitHub repository object.
    cname : str
        The canonical domain name where documentation was deployed.
    removed_prs : list[str]
        List of PR numbers that had their documentation removed.
    """
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
