# Copyright (C) 2022 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Automate patch/minor/major releases by bumping a version and pushing git tags."""

import ast
import os
from pathlib import Path
import re
import subprocess
import sys

from packaging.version import Version
import tomlkit


class AutoReleaseError(Exception):
    """Raised for a fatal, user-facing hk-autorelease failure."""


def _constant_str_value(node: ast.AST | None) -> str | None:
    """Return the string value of an ``ast.Constant`` node, or ``None`` if not a str constant."""
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _find_setup_py_version_node(tree: ast.Module) -> ast.Constant | None:
    """Find the ``version=`` keyword argument's string-constant node in a ``setup(...)`` call."""
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call):
            continue
        func = node.func
        is_setup_call = (isinstance(func, ast.Name) and func.id == "setup") or (
            isinstance(func, ast.Attribute) and func.attr == "setup"
        )
        if not is_setup_call:
            continue
        for keyword in node.keywords:
            if (
                keyword.arg == "version"
                and isinstance(keyword.value, ast.Constant)
                and _constant_str_value(keyword.value) is not None
            ):
                return keyword.value
    return None


def _find_python_module_version_node(tree: ast.Module) -> ast.Constant | None:
    """Find the top-level ``__version__`` assignment's string-constant node."""
    for node in tree.body:
        if isinstance(node, ast.Assign):
            targets = node.targets
            value = node.value
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
            value = node.value
        else:
            continue
        if any(isinstance(target, ast.Name) and target.id == "__version__" for target in targets):
            if isinstance(value, ast.Constant) and _constant_str_value(value) is not None:
                return value
    return None


def _parse_python_source(location: str, text: str) -> ast.Module:
    """Parse ``text`` as Python, raising ``AutoReleaseError`` (not ``SyntaxError``) on failure."""
    try:
        return ast.parse(text)
    except SyntaxError as error:
        raise AutoReleaseError(f"Could not parse '{location}' as Python: {error}") from error


def _splice_string_constant(text: str, node: ast.Constant, new_value: str) -> str:
    """Replace the exact source span of a string-constant node with a new, same-quoted value."""
    if node.lineno != node.end_lineno:
        raise AutoReleaseError("Version string literal must be on a single line.")
    lines = text.splitlines(keepends=True)
    line = lines[node.lineno - 1]
    quote = line[node.col_offset]
    new_line = line[: node.col_offset] + f"{quote}{new_value}{quote}" + line[node.end_col_offset :]
    lines[node.lineno - 1] = new_line
    return "".join(lines)


def read_version(source: str, location: str) -> str:
    """Read the current version string from ``location`` using ``source`` rules."""
    path = Path(location)
    if not path.is_file():
        raise AutoReleaseError(f"version-location '{location}' does not exist.")
    text = path.read_text(encoding="utf-8")

    if source == "file":
        version = text.strip()
    elif source == "pyproject":
        version = tomlkit.parse(text).get("project", {}).get("version")
    elif source == "setup-py":
        tree = _parse_python_source(location, text)
        node = _find_setup_py_version_node(tree)
        version = node.value if node is not None else None
    elif source == "python-module":
        tree = _parse_python_source(location, text)
        node = _find_python_module_version_node(tree)
        version = node.value if node is not None else None
    else:
        raise AutoReleaseError(f"Unknown version-source '{source}'.")

    if not version:
        raise AutoReleaseError(
            f"Could not find a version string in '{location}' (version-source: '{source}')."
        )
    return str(version)


def write_version(source: str, location: str, new_version: str) -> None:
    """Write ``new_version`` to ``location`` using ``source`` rules."""
    path = Path(location)

    if source == "file":
        path.write_text(f"{new_version}\n", encoding="utf-8")
        return

    if source == "pyproject":
        document = tomlkit.parse(path.read_text(encoding="utf-8"))
        document["project"]["version"] = new_version
        path.write_text(tomlkit.dumps(document), encoding="utf-8")
        return

    if source in ("setup-py", "python-module"):
        text = path.read_text(encoding="utf-8")
        tree = _parse_python_source(location, text)
        finder = (
            _find_setup_py_version_node
            if source == "setup-py"
            else _find_python_module_version_node
        )
        node = finder(tree)
        if node is None:
            raise AutoReleaseError(
                f"Could not find a version string in '{location}' (version-source: '{source}')."
            )
        new_text = _splice_string_constant(text, node, new_version)
        path.write_text(new_text, encoding="utf-8")
        return

    raise AutoReleaseError(f"Unknown version-source '{source}'.")


def release_branch_name(branch_prefix: str, major: int, minor: int) -> str:
    """Compute the release branch name for a given ``major.minor`` version."""
    return f"{branch_prefix}{major}.{minor}"


def bump_minor_major(current_dev_version: str, release_type: str, branch_prefix: str):
    """Compute the release version, next dev version, and release branch.

    Returns
    -------
    tuple[str, str, str]
        ``(release_version, dev_version, release_branch)``.
    """
    version = Version(current_dev_version)
    major, minor = version.major, version.minor

    if release_type == "major":
        new_major = major + 1
        release_version = f"{new_major}.0.0"
        dev_version = f"{new_major}.1.dev0"
        branch = release_branch_name(branch_prefix, new_major, 0)
    elif release_type == "minor":
        release_version = f"{major}.{minor}.0"
        dev_version = f"{major}.{minor + 1}.dev0"
        branch = release_branch_name(branch_prefix, major, minor)
    else:
        raise AutoReleaseError(f"bump_minor_major does not support release-type '{release_type}'.")

    return release_version, dev_version, branch


def require_dev_version(version: str, branch: str) -> None:
    """Raise ``AutoReleaseError`` if ``version`` is not a development release."""
    if not Version(version).is_devrelease:
        raise AutoReleaseError(
            f"Expected a development version (e.g. 'X.Y.devN') on branch '{branch}' before a "
            f"minor/major release, but found '{version}'. Did a previous release already bump "
            "this version?"
        )


def dev_version_bump_pr_title(dev_version: str) -> str:
    """Return the pull request title for a dev-version-bump PR."""
    return f"chore: bump dev version to v{dev_version}"


def dev_version_bump_pr_body(release_version: str) -> str:
    """Return the pull request body for a dev-version-bump PR."""
    return (
        f"Automated dev-version bump after cutting release `v{release_version}`.\n\n"
        "> [!CAUTION]\n"
        f"> Do not merge this pull request until the `v{release_version}` release has been "
        "successfully published (for example via the `release-github`/`release-pypi-public` "
        "actions). Merging it early will not break the release, but you should confirm the "
        "release succeeded first.\n"
    )


def create_dev_version_bump_pr(
    main_branch: str, bump_branch: str, release_version: str, dev_version: str
) -> str:
    """Open a draft pull request bumping the dev version on ``main_branch``.

    Returns
    -------
    str
        The URL of the created pull request.
    """
    result = subprocess.run(
        [
            "gh",
            "pr",
            "create",
            "--draft",
            "--title",
            dev_version_bump_pr_title(dev_version),
            "--body",
            dev_version_bump_pr_body(release_version),
            "--base",
            main_branch,
            "--head",
            bump_branch,
        ],
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise AutoReleaseError(
            f"Failed to create dev-version bump pull request:\n{result.stdout}\n{result.stderr}"
        )
    return result.stdout.strip()


def bump_patch(current_release_version: str) -> str:
    """Bump the patch component of ``current_release_version``."""
    version = Version(current_release_version)
    return f"{version.major}.{version.minor}.{version.micro + 1}"


def ref_exists_on_remote(ref: str) -> bool:
    """Return ``True`` if ``ref`` already exists on the ``origin`` remote."""
    result = subprocess.run(
        ["git", "ls-remote", "--exit-code", "origin", ref], capture_output=True, text=True
    )
    return result.returncode == 0


def require_refs_available(*refs: str) -> None:
    """Raise ``AutoReleaseError`` if any of ``refs`` already exists on the ``origin`` remote."""
    existing = [ref for ref in refs if ref_exists_on_remote(ref)]
    if existing:
        raise AutoReleaseError(
            "Refusing to start: the following refs already exist on 'origin': "
            f"{', '.join(existing)}. This may be left over from a previous, partially-failed "
            "run -- delete them manually once you've confirmed it's safe to retry."
        )


def parse_latest_release_tag(tag_lines: list[str]) -> tuple[int, int, int]:
    """Return the ``(major, minor, patch)`` of the first ``vX.Y.Z`` tag in ``tag_lines``.

    ``tag_lines`` is expected to already be sorted from newest to oldest, as
    produced by ``git tag --list "v*" --sort=-version:refname``.
    """
    tag_pattern = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
    for tag in tag_lines:
        match = tag_pattern.match(tag.strip())
        if match:
            major, minor, patch = match.groups()
            return int(major), int(minor), int(patch)
    raise AutoReleaseError("No 'vX.Y.Z' tags found; cannot perform a patch release.")


def classify_merge_conflict(conflicted_files: list[str], version_location: str) -> bool:
    """Return ``True`` if the only conflicting file is ``version_location``."""
    return conflicted_files == [version_location]


def run_git(*args: str, check: bool = True) -> str:
    """Run a git command and return its stripped stdout."""
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and result.returncode != 0:
        raise AutoReleaseError(f"git {' '.join(args)} failed:\n{result.stdout}\n{result.stderr}")
    return result.stdout.strip()


def export_output(name: str, value: str) -> None:
    """Append a ``name=value`` entry to the ``GITHUB_OUTPUT`` file."""
    github_output = os.environ["GITHUB_OUTPUT"]
    with Path(github_output).open("a", encoding="utf-8") as file:
        file.write(f"{name}={value}\n")


def find_latest_release_tag() -> tuple[int, int, int]:
    """Fetch tags and return the ``(major, minor, patch)`` of the latest release."""
    run_git("fetch", "--tags")
    output = run_git("tag", "--list", "v*", "--sort=-version:refname")
    return parse_latest_release_tag(output.splitlines())


def merge_main_into_release(main_branch: str, version_location: str) -> None:
    """Merge ``main_branch`` into the current branch, auto-resolving version-only conflicts."""
    result = subprocess.run(
        ["git", "merge", main_branch, "--no-edit"], capture_output=True, text=True
    )
    if result.returncode == 0:
        return

    conflicted = run_git("diff", "--name-only", "--diff-filter=U").splitlines()
    if classify_merge_conflict(conflicted, version_location):
        run_git("checkout", "--ours", version_location)
        run_git("add", version_location)
        run_git("commit", "--no-edit")
        return

    run_git("merge", "--abort", check=False)
    raise AutoReleaseError(
        "Merge conflicts detected outside of the version file: "
        f"{', '.join(conflicted) or 'unknown'}. Please resolve manually.\n"
        f"git merge output:\n{result.stdout}\n{result.stderr}"
    )


def cherry_pick_commits_into_release(commits: list[str], version_location: str) -> None:
    """Cherry-pick each of ``commits`` onto the current branch, in order.

    Auto-resolves a conflict the same way ``merge_main_into_release`` does, if it's limited
    to ``version_location``; aborts with a clear error otherwise.
    """
    for commit in commits:
        result = subprocess.run(["git", "cherry-pick", commit], capture_output=True, text=True)
        if result.returncode == 0:
            continue

        conflicted = run_git("diff", "--name-only", "--diff-filter=U").splitlines()
        if classify_merge_conflict(conflicted, version_location):
            run_git("checkout", "--ours", version_location)
            run_git("add", version_location)
            run_git("cherry-pick", "--continue")
            continue

        run_git("cherry-pick", "--abort", check=False)
        raise AutoReleaseError(
            f"Cherry-pick of commit '{commit}' produced conflicts outside of the version "
            f"file: {', '.join(conflicted) or 'unknown'}. Please resolve manually.\n"
            f"git cherry-pick output:\n{result.stdout}\n{result.stderr}"
        )


def run_minor_major_release(
    release_type, version_source, version_location, main_branch, branch_prefix
):
    """Perform a minor or major release.

    Returns
    -------
    tuple[str, str, str, str]
        ``(release_version, dev_version, branch, dev_version_pr_url)``.
    """
    run_git("checkout", main_branch)
    run_git("pull")

    current_dev_version = read_version(version_source, version_location)
    require_dev_version(current_dev_version, main_branch)
    release_version, dev_version, branch = bump_minor_major(
        current_dev_version, release_type, branch_prefix
    )
    bump_branch = f"chore/bump-dev-version-v{dev_version}"
    require_refs_available(
        f"refs/heads/{branch}", f"refs/tags/v{release_version}", f"refs/heads/{bump_branch}"
    )

    run_git("checkout", "-b", branch)
    write_version(version_source, version_location, release_version)
    run_git("add", version_location)
    run_git("commit", "-m", f"release: v{release_version}")
    run_git("push", "origin", branch)
    run_git("tag", f"v{release_version}")
    run_git("push", "origin", f"v{release_version}")

    run_git("checkout", main_branch)
    run_git("checkout", "-b", bump_branch)
    write_version(version_source, version_location, dev_version)
    run_git("add", version_location)
    run_git("commit", "-m", dev_version_bump_pr_title(dev_version))
    run_git("push", "origin", bump_branch)
    dev_version_pr_url = create_dev_version_bump_pr(
        main_branch, bump_branch, release_version, dev_version
    )

    return release_version, dev_version, branch, dev_version_pr_url


def _finish_patch_release(
    version_source, version_location, main_branch, branch_prefix, apply_changes
):
    """Shared tail end of a patch release, once the release-branch content is ready to bump.

    Parameters
    ----------
    version_source : str
        Where the version is stored (``file``, ``pyproject``, ``setup-py``, or
        ``python-module``).
    version_location : str
        Path to the file identified by ``version_source``.
    main_branch : str
        Name of the main development branch.
    branch_prefix : str
        Prefix used to compute the release branch name.
    apply_changes : Callable[[], None]
        Called with the release branch checked out, to bring in the desired changes (merge
        all of main, or cherry-pick specific commits) before the version is bumped.

    Returns
    -------
    tuple[str, str]
        ``(release_version, release_branch)``.
    """
    run_git("checkout", main_branch)
    run_git("pull")

    major, minor, _patch = find_latest_release_tag()
    branch = release_branch_name(branch_prefix, major, minor)

    run_git("checkout", branch)
    apply_changes()

    current_version = read_version(version_source, version_location)
    release_version = bump_patch(current_version)
    require_refs_available(f"refs/tags/v{release_version}")
    write_version(version_source, version_location, release_version)
    run_git("add", version_location)
    run_git("commit", "-m", f"release: v{release_version}")
    run_git("push", "origin", branch)
    run_git("tag", f"v{release_version}")
    run_git("push", "origin", f"v{release_version}")

    run_git("checkout", main_branch)

    return release_version, branch


def run_patch_release(version_source, version_location, main_branch, branch_prefix):
    """Perform a patch release by merging all of main into the release branch.

    Returns
    -------
    tuple[str, str]
        ``(release_version, release_branch)``.
    """
    return _finish_patch_release(
        version_source,
        version_location,
        main_branch,
        branch_prefix,
        lambda: merge_main_into_release(main_branch, version_location),
    )


def run_patch_cherry_pick_release(
    version_source, version_location, main_branch, branch_prefix, commits
):
    """Perform a patch release by cherry-picking specific commits onto the release branch.

    Parameters
    ----------
    commits : list[str]
        Commit SHAs to cherry-pick, in order.

    Returns
    -------
    tuple[str, str]
        ``(release_version, release_branch)``.
    """
    return _finish_patch_release(
        version_source,
        version_location,
        main_branch,
        branch_prefix,
        lambda: cherry_pick_commits_into_release(commits, version_location),
    )


def require_env(name: str) -> str:
    """Return the value of environment variable ``name``, or raise ``AutoReleaseError``."""
    try:
        return os.environ[name]
    except KeyError:
        raise AutoReleaseError(f"Missing required environment variable '{name}'.") from None


def main() -> None:
    """Entry point: read inputs from the environment and perform the release."""
    valid_release_types = ("patch", "patch-cherry-pick", "minor", "major")
    valid_version_sources = ("file", "pyproject", "setup-py", "python-module")

    release_type = require_env("RELEASE_TYPE")
    version_source = require_env("VERSION_SOURCE")
    version_location = require_env("VERSION_LOCATION")
    main_branch = require_env("MAIN_BRANCH")
    branch_prefix = require_env("RELEASE_BRANCH_PREFIX")

    if release_type not in valid_release_types:
        raise AutoReleaseError(
            f"Invalid release-type '{release_type}'. Must be one of {valid_release_types}."
        )
    if version_source not in valid_version_sources:
        raise AutoReleaseError(
            f"Invalid version-source '{version_source}'. Must be one of {valid_version_sources}."
        )

    if release_type == "patch":
        release_version, branch = run_patch_release(
            version_source, version_location, main_branch, branch_prefix
        )
        dev_version = ""
        dev_version_pr_url = ""
    elif release_type == "patch-cherry-pick":
        commits = [
            commit.strip()
            for commit in require_env("CHERRY_PICK_COMMITS").split(",")
            if commit.strip()
        ]
        if not commits:
            raise AutoReleaseError(
                "release-type 'patch-cherry-pick' requires at least one commit SHA in "
                "'cherry-pick-commits'."
            )
        release_version, branch = run_patch_cherry_pick_release(
            version_source, version_location, main_branch, branch_prefix, commits
        )
        dev_version = ""
        dev_version_pr_url = ""
    else:
        release_version, dev_version, branch, dev_version_pr_url = run_minor_major_release(
            release_type, version_source, version_location, main_branch, branch_prefix
        )

    export_output("new-version", release_version)
    export_output("new-dev-version", dev_version)
    export_output("release-branch", branch)
    export_output("dev-version-pr-url", dev_version_pr_url)


if __name__ == "__main__":
    try:
        main()
    except AutoReleaseError as error:
        print(f"::error::{error}", file=sys.stderr)
        sys.exit(1)
