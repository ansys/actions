from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import TYPE_CHECKING, NamedTuple

from github import Auth, Github, UnknownObjectException

if TYPE_CHECKING:
    from github.Repository import Repository

PR_COMMENT = (
    "This PR has been closed. Documentation for this pull request will shortly be removed from its "
    "[former deployment address](https://{cname}/pull/{pr_number})."
)


class Config(NamedTuple):
    """Configuration data from environment variables."""

    token: str
    repo_slug: str
    branch: str
    cname: str


def get_config() -> Config:
    """Get all required configuration from environment variables.

    Returns
    -------
    Config
        Configuration object containing token, repo_slug, branch, and cname.

    Raises
    ------
    Exception
        If any required environment variable is missing.
    """
    missing_vars = []

    token = os.environ.get("GITHUB_TOKEN", "")
    if not token:
        missing_vars.append("GITHUB_TOKEN")

    repo_slug = os.environ.get("GITHUB_REPOSITORY", "")
    if not repo_slug:
        missing_vars.append("GITHUB_REPOSITORY")

    branch = os.environ.get("BRANCH", "")
    if not branch:
        missing_vars.append("BRANCH")

    cname = os.environ.get("CNAME", "")
    if not cname:
        missing_vars.append("CNAME")

    if missing_vars:
        raise Exception(f"Missing environment variables: {', '.join(missing_vars)}")

    return Config(token=token, repo_slug=repo_slug, branch=branch, cname=cname)


def get_prs_to_cleanup(repo: Repository, branch: str) -> list[str]:
    """Identify PR numbers that need documentation cleanup.

    Compares deployed PR documentation with currently opened PRs to identify
    closed PRs that still have deployed documentation.

    Parameters
    ----------
    repo : Repository
        GitHub repository object.
    branch : str
        The branch name to retrieve deployed documentation from.

    Returns
    -------
    list[str]
        List of PR numbers for closed PRs that have deployed
        documentation and should be removed.
    """
    try:
        deployed_pr_docs = repo.get_contents(path="pull", ref=branch)
        # Ensure we always have a list
        if not isinstance(deployed_pr_docs, list):
            deployed_pr_docs = [deployed_pr_docs]
    except UnknownObjectException:  # means pull/ is not present
        return []

    # Extract deployed PR numbers
    deployed_pr_nums = [
        content.path.removeprefix("pull/") for content in deployed_pr_docs
    ]

    # Get opened PR numbers
    opened_prs = repo.get_pulls(state="opened")
    opened_pr_nums = [str(pr.number) for pr in opened_prs]

    # Find closed PRs with deployed documentation
    closed_prs_with_deployed_doc = list(set(deployed_pr_nums) - set(opened_pr_nums))
    return closed_prs_with_deployed_doc


def cleanup_pr_documentation(repo: Repository, cname: str, pr_numbers: list[str]):
    """Remove PR documentation and add notification comments.

    Removes the local documentation directories for the given PR numbers
    and posts notification comments on the closed PRs.

    Parameters
    ----------
    repo : Repository
        GitHub repository object.
    cname : str
        The canonical domain name where documentation was deployed.
    pr_numbers : list[str]
        List of PR numbers whose documentation should be removed.
    """
    if not pr_numbers:
        return

    # Remove documentation directories
    pull_path = Path("pull")
    for pr_number in pr_numbers:
        shutil.rmtree(pull_path / pr_number)

    # Remove pull directory if empty
    if len(os.listdir(pull_path)) == 0:
        pull_path.rmdir()

    # Add notification comments to closed PRs
    for pr_number in pr_numbers:
        issue = repo.get_issue(number=int(pr_number))
        issue.create_comment(PR_COMMENT.format(cname=cname, pr_number=pr_number))


if __name__ == "__main__":
    # Get configuration
    config = get_config()

    # Initialize GitHub API
    auth = Auth.Token(config.token)
    gh = Github(auth=auth)
    repo = gh.get_repo(config.repo_slug)

    # Find PRs that need cleanup
    prs_to_remove = get_prs_to_cleanup(repo, config.branch)

    # Perform cleanup
    cleanup_pr_documentation(repo, config.cname, prs_to_remove)
