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
from collections.abc import Callable, Iterator
from contextlib import contextmanager
import os
from pathlib import Path
import re
import subprocess
import sys

from packaging.version import Version
import tomlkit


class AutoReleaseError(Exception):
    """Raised for a fatal, user-facing hk-autorelease failure."""


def log_progress(message: str) -> None:
    """Print a progress message immediately so it is visible in CI logs."""
    print(f"[hk-autorelease] {message}", flush=True)


def _constant_str_value(node: ast.AST | None) -> str | None:
    """Return the string value of an ``ast.Constant`` node, or ``None`` if not a str constant.

    Parameters
    ----------
    node : ast.AST | None
        The AST node to inspect.

    Returns
    -------
    str | None
        The string value, or ``None`` if ``node`` isn't a string constant.
    """
    if isinstance(node, ast.Constant) and isinstance(node.value, str):
        return node.value
    return None


def _find_setup_py_version_node(tree: ast.Module) -> ast.Constant | None:
    """Find the ``version=`` keyword argument's string-constant node in a ``setup(...)`` call.

    Parameters
    ----------
    tree : ast.Module
        The parsed AST of a ``setup.py`` file.

    Returns
    -------
    ast.Constant | None
        The string-constant node for the ``version=`` keyword argument, or ``None`` if no
        ``setup(...)`` call with a string ``version=`` keyword argument was found.
    """
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
    """Find the top-level ``__version__`` assignment's string-constant node.

    Parameters
    ----------
    tree : ast.Module
        The parsed AST of a Python module.

    Returns
    -------
    ast.Constant | None
        The string-constant node assigned to ``__version__``, or ``None`` if no top-level
        ``__version__`` assignment with a string value was found.
    """
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
    """Parse ``text`` as Python, raising ``AutoReleaseError`` (not ``SyntaxError``) on failure.

    Parameters
    ----------
    location : str
        Path of the file ``text`` was read from, used only for the error message.
    text : str
        The Python source code to parse.

    Returns
    -------
    ast.Module
        The parsed AST.
    """
    try:
        return ast.parse(text)
    except SyntaxError as error:
        raise AutoReleaseError(f"Could not parse '{location}' as Python: {error}") from error


def _splice_string_constant(text: str, node: ast.Constant, new_value: str) -> str:
    """Replace the exact source span of a string-constant node with a new, same-quoted value.

    Parameters
    ----------
    text : str
        The full source text containing ``node``.
    node : ast.Constant
        The string-constant AST node to replace.
    new_value : str
        The new string value to splice in, reusing ``node``'s original quote character.

    Returns
    -------
    str
        ``text`` with ``node``'s source span replaced.
    """
    if node.lineno != node.end_lineno:
        raise AutoReleaseError("Version string literal must be on a single line.")
    lines = text.splitlines(keepends=True)
    line = lines[node.lineno - 1]
    quote = line[node.col_offset]
    new_line = line[: node.col_offset] + f"{quote}{new_value}{quote}" + line[node.end_col_offset :]
    lines[node.lineno - 1] = new_line
    return "".join(lines)


def read_version(source: str, location: str) -> str:
    """Read the current version string from ``location`` using ``source`` rules.

    Parameters
    ----------
    source : str
        Where the version is stored: ``file``, ``pyproject``, ``setup-py``, or
        ``python-module``.
    location : str
        Path to the file identified by ``source``.

    Returns
    -------
    str
        The current version string.
    """
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
    """Write ``new_version`` to ``location`` using ``source`` rules.

    Parameters
    ----------
    source : str
        Where the version is stored: ``file``, ``pyproject``, ``setup-py``, or
        ``python-module``.
    location : str
        Path to the file identified by ``source``.
    new_version : str
        The new version string to write.
    """
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


def update_lock_file(lock_file_tool: str, version_location: str) -> str | None:
    """Regenerate the dependency lock file for ``lock_file_tool``, without upgrading anything.

    The lock command runs in the directory of the nearest ``pyproject.toml`` found at or above
    ``version_location``'s directory (without going above the repository root), so the lock
    file is regenerated next to that ``pyproject.toml``.

    Parameters
    ----------
    lock_file_tool : str
        Which lock file tooling to use: ``none``, ``uv``, or ``poetry``.
    version_location : str
        Path, relative to the repository root, to the file holding the version.

    Returns
    -------
    str | None
        Path, relative to the repository root, to the lock file that was regenerated, or
        ``None`` if ``lock_file_tool`` is ``"none"``.
    """
    if lock_file_tool == "none":
        log_progress("Skipping lock file regeneration (lock-file-tool: none).")
        return None

    commands = {
        "uv": ["uv", "lock"],
        "poetry": ["uvx", "poetry", "lock", "--no-update"],
    }
    lock_files = {
        "uv": "uv.lock",
        "poetry": "poetry.lock",
    }
    if lock_file_tool not in commands:
        raise AutoReleaseError(f"Unknown lock-file-tool '{lock_file_tool}'.")

    repo_root = Path.cwd().resolve()
    project_dir = (repo_root / version_location).parent.resolve()
    while not (project_dir / "pyproject.toml").is_file():
        if project_dir == repo_root or project_dir == project_dir.parent:
            raise AutoReleaseError(
                f"Could not find a 'pyproject.toml' at or above '{version_location}' to "
                f"regenerate the '{lock_file_tool}' lock file."
            )
        project_dir = project_dir.parent

    command = commands[lock_file_tool]
    lock_file = (project_dir / lock_files[lock_file_tool]).relative_to(repo_root).as_posix()
    log_progress(f"Regenerating '{lock_file}' using {lock_file_tool} in '{project_dir}'.")
    result = subprocess.run(command, capture_output=True, text=True, cwd=project_dir)
    if result.returncode != 0:
        raise AutoReleaseError(
            f"Failed to update '{lock_file}' via '{' '.join(command)}':\n"
            f"{result.stdout}\n{result.stderr}"
        )
    return lock_file


def release_branch_name(branch_prefix: str, major: int, minor: int) -> str:
    """Compute the release branch name for a given ``major.minor`` version.

    Parameters
    ----------
    branch_prefix : str
        Prefix prepended to the computed branch name.
    major : int
        Major version component.
    minor : int
        Minor version component.

    Returns
    -------
    str
        The release branch name, ``<branch_prefix><major>.<minor>``.
    """
    return f"{branch_prefix}{major}.{minor}"


def bump_minor_major(
    current_dev_version: str, release_type: str, branch_prefix: str
) -> tuple[str, str, str]:
    """Compute the release version, next dev version, and release branch.

    Parameters
    ----------
    current_dev_version : str
        Current development version on the main branch, for example ``0.2.dev0``.
    release_type : str
        Either ``"minor"`` or ``"major"``.
    branch_prefix : str
        Prefix used to build the release branch name.

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
    """Raise ``AutoReleaseError`` if ``version`` is not a development release.

    Parameters
    ----------
    version : str
        The version string to check.
    branch : str
        Name of the branch ``version`` was read from, used only for the error message.
    """
    if not Version(version).is_devrelease:
        raise AutoReleaseError(
            f"Expected a development version (e.g. 'X.Y.devN') on branch '{branch}' before a "
            f"minor/major release, but found '{version}'. Did a previous release already bump "
            "this version?"
        )


def dev_version_bump_pr_title(dev_version: str) -> str:
    """Return the pull request title for a dev-version-bump PR.

    Parameters
    ----------
    dev_version : str
        The new development version being bumped to.

    Returns
    -------
    str
        The pull request title.
    """
    return f"chore: bump dev version to v{dev_version}"


def dev_version_bump_pr_body(release_version: str) -> str:
    """Return the pull request body for a dev-version-bump PR.

    Parameters
    ----------
    release_version : str
        The release version that was just cut, referenced in the cautionary note.

    Returns
    -------
    str
        The pull request body, including a caution note about publishing order.
    """
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

    Parameters
    ----------
    main_branch : str
        Name of the main development branch, used as the pull request's base.
    bump_branch : str
        Name of the branch carrying the dev-version bump commit, used as the pull request's
        head.
    release_version : str
        The release version that was just cut.
    dev_version : str
        The new development version being bumped to.

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
            f"Failed to create dev-version bump pull request:\n{result.stdout}\n{result.stderr}\n"
            "The request may have succeeded remotely despite this error; verify whether the "
            "pull request exists before retrying."
        )
    return result.stdout.strip()


def bump_patch(current_release_version: str) -> str:
    """Bump the patch component of ``current_release_version``.

    Parameters
    ----------
    current_release_version : str
        The current release version, for example ``0.2.0``.

    Returns
    -------
    str
        The version with its patch component incremented by one.
    """
    version = Version(current_release_version)
    return f"{version.major}.{version.minor}.{version.micro + 1}"


def ref_exists_on_remote(ref: str) -> bool:
    """Return ``True`` if ``ref`` already exists on the ``origin`` remote.

    Parameters
    ----------
    ref : str
        Full ref name to check, for example ``refs/heads/release/1.2`` or ``refs/tags/v1.2.0``.

    Returns
    -------
    bool
        ``True`` if ``ref`` exists on ``origin``.
    """
    result = subprocess.run(
        ["git", "ls-remote", "--exit-code", "origin", ref], capture_output=True, text=True
    )
    if result.returncode == 0:
        return True
    if result.returncode == 2:
        return False
    raise AutoReleaseError(f"git ls-remote origin {ref} failed:\n{result.stdout}\n{result.stderr}")


def require_refs_available(*refs: str) -> None:
    """Raise ``AutoReleaseError`` if any of ``refs`` already exists on the ``origin`` remote.

    Parameters
    ----------
    *refs : str
        Full ref names to check.
    """
    log_progress(f"Checking that release refs are available on origin: {', '.join(refs)}.")
    existing = [ref for ref in refs if ref_exists_on_remote(ref)]
    if existing:
        raise AutoReleaseError(
            "Refusing to start: the following refs already exist on 'origin': "
            f"{', '.join(existing)}. This may be left over from a previous, partially-failed "
            "run -- delete them manually once you've confirmed it's safe to retry."
        )


def _remote_ref_sha(ref: str) -> str:
    """Return the SHA of ``ref`` on origin, or an empty string if it is absent."""
    result = run_git("ls-remote", "origin", ref)
    return result.split("\t", 1)[0] if result else ""


class ReleaseJournal:
    """Record remote writes so they can be safely compensated if release processing fails."""

    def __init__(self) -> None:
        self._undo_steps: list[tuple[str, Callable[[], None]]] = []

    def push_branch(self, branch: str) -> None:
        """Push a branch with a lease and record a guarded restoration before the write."""
        ref = f"refs/heads/{branch}"
        if _remote_ref_sha(ref):
            run_git("fetch", "--no-tags", "origin", ref)
        previous = _remote_ref_sha(ref)
        new_sha = run_git("rev-parse", branch)

        if previous:
            ancestor = subprocess.run(
                ["git", "merge-base", "--is-ancestor", previous, new_sha],
                capture_output=True,
                text=True,
            )
            if ancestor.returncode != 0:
                raise AutoReleaseError(
                    f"Refusing to update remote branch '{branch}': local commit {new_sha} is "
                    f"not a descendant of remote commit {previous}."
                )

        self._undo_steps.append(
            (
                (
                    f"reset branch '{branch}' to {previous}"
                    if previous
                    else f"delete branch '{branch}'"
                ),
                lambda: self._restore_branch(ref, branch, previous, new_sha),
            )
        )
        run_git(
            "push",
            f"--force-with-lease={ref}:{previous}",
            "origin",
            f"{branch}:{ref}",
        )

    @staticmethod
    def _restore_branch(ref: str, branch: str, previous: str, new_sha: str) -> None:
        current = _remote_ref_sha(ref)
        if current == previous:
            return
        if current != new_sha:
            raise AutoReleaseError(
                f"Remote branch '{branch}' is now at {current or 'no ref'}, not this run's "
                f"commit {new_sha}; preserving the remote change."
            )
        refspec = f"{previous}:{ref}" if previous else f":{ref}"
        run_git(
            "push",
            f"--force-with-lease={ref}:{new_sha}",
            "origin",
            refspec,
        )

    def push_tag(self, tag: str) -> None:
        """Push a new tag and record conditional deletion of only this run's tag."""
        ref = f"refs/tags/{tag}"
        if _remote_ref_sha(ref):
            raise AutoReleaseError(f"Refusing to overwrite existing remote tag '{tag}'.")
        new_sha = run_git("rev-parse", ref)
        self._undo_steps.append(
            (f"delete tag '{tag}'", lambda: self._delete_tag(ref, tag, new_sha))
        )
        run_git("push", f"--force-with-lease={ref}:", "origin", f"{ref}:{ref}")

    def record_local_tag(self, tag: str) -> None:
        """Record deletion of this run's local tag if it still points to the same object."""
        ref = f"refs/tags/{tag}"
        tag_sha = run_git("rev-parse", ref)

        def delete() -> None:
            result = subprocess.run(
                ["git", "rev-parse", "--verify", ref], capture_output=True, text=True
            )
            if result.returncode != 0:
                return
            if result.stdout.strip() != tag_sha:
                raise AutoReleaseError(
                    f"Local tag '{tag}' changed after this run created it; preserving the tag."
                )
            run_git("tag", "-d", tag)

        self._undo_steps.append((f"delete local tag '{tag}'", delete))

    @staticmethod
    def _delete_tag(ref: str, tag: str, new_sha: str) -> None:
        current = _remote_ref_sha(ref)
        if not current:
            return
        if current != new_sha:
            raise AutoReleaseError(
                f"Remote tag '{tag}' is now at {current}, not this run's tag {new_sha}; "
                "preserving the remote tag."
            )
        run_git(
            "push",
            f"--force-with-lease={ref}:{new_sha}",
            "origin",
            f":{ref}",
        )

    def record_pull_request(self, url: str) -> None:
        """Record a successfully created pull request so it can be closed."""

        def close() -> None:
            result = subprocess.run(["gh", "pr", "close", url], capture_output=True, text=True)
            if result.returncode != 0:
                raise AutoReleaseError(f"{result.stdout}\n{result.stderr}")

        self._undo_steps.append((f"close pull request {url}", close))

    def rollback(self) -> str:
        """Undo recorded writes newest-first and report every success or failure."""
        report = []
        for description, undo in reversed(self._undo_steps):
            try:
                undo()
                report.append(f"- rolled back: {description} (or already in its original state)")
            except Exception as error:
                report.append(f"- FAILED to {description} (fix manually): {error}")
        self._undo_steps.clear()
        return "Rollback report:\n" + "\n".join(report) if report else ""


@contextmanager
def rollback_on_failure() -> Iterator[ReleaseJournal]:
    """Compensate for recorded remote writes when release processing fails."""
    journal = ReleaseJournal()
    try:
        yield journal
    except Exception as error:
        report = journal.rollback()
        if not report:
            raise
        raise AutoReleaseError(f"{error}\n\n{report}") from error


def parse_latest_release_tag(tag_lines: list[str]) -> tuple[int, int, int]:
    """Return the ``(major, minor, patch)`` of the first ``vX.Y.Z`` tag in ``tag_lines``.

    ``tag_lines`` is expected to already be sorted from newest to oldest, as
    produced by ``git tag --list "v*" --sort=-version:refname``.

    Parameters
    ----------
    tag_lines : list[str]
        Tag names, newest first.

    Returns
    -------
    tuple[int, int, int]
        The ``(major, minor, patch)`` of the first matching tag.
    """
    tag_pattern = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")
    for tag in tag_lines:
        match = tag_pattern.match(tag.strip())
        if match:
            major, minor, patch = match.groups()
            return int(major), int(minor), int(patch)
    raise AutoReleaseError("No 'vX.Y.Z' tags found; cannot perform a patch release.")


def classify_merge_conflict(conflicted_files: list[str], version_location: str) -> bool:
    """Return ``True`` if the conflicts are limited to the version file and/or lock files.

    Parameters
    ----------
    conflicted_files : list[str]
        Paths reported as unmerged/conflicting by git.
    version_location : str
        Path to the version file.

    Returns
    -------
    bool
        ``True`` if ``conflicted_files`` is non-empty and only contains ``version_location``
        and/or ``uv.lock``/``poetry.lock`` files.
    """
    return bool(conflicted_files) and all(
        path == version_location or Path(path).name in ("uv.lock", "poetry.lock")
        for path in conflicted_files
    )


def keep_ours_in_conflicts(path: str) -> None:
    """Resolve each conflict hunk in ``path`` by keeping the current branch's side, then stage it.

    Non-conflicting changes already merged into the file are left untouched.

    Parameters
    ----------
    path : str
        Path to a file containing git conflict markers.
    """
    log_progress(f"Resolving conflicts in '{path}' by keeping the release branch's hunks.")
    file = Path(path)
    kept = []
    side = None
    for line in file.read_text(encoding="utf-8").splitlines(keepends=True):
        if line.startswith("<<<<<<<"):
            side = "ours"
        elif side and line.startswith("|||||||"):
            side = "base"
        elif side and line.startswith("======="):
            side = "theirs"
        elif side and line.startswith(">>>>>>>"):
            side = None
        elif side in (None, "ours"):
            kept.append(line)
    file.write_text("".join(kept), encoding="utf-8", newline="")
    run_git("add", path)


def run_git(*args: str, check: bool = True) -> str:
    """Run a git command and return its stripped stdout.

    Parameters
    ----------
    *args : str
        Arguments passed to ``git``.
    check : bool
        If ``True`` (the default), raise ``AutoReleaseError`` when the command exits non-zero.

    Returns
    -------
    str
        The command's stripped stdout.
    """
    result = subprocess.run(["git", *args], capture_output=True, text=True)
    if check and result.returncode != 0:
        raise AutoReleaseError(f"git {' '.join(args)} failed:\n{result.stdout}\n{result.stderr}")
    return result.stdout.strip()


def export_output(name: str, value: str) -> None:
    """Append a ``name=value`` entry to the ``GITHUB_OUTPUT`` file.

    Parameters
    ----------
    name : str
        The output name.
    value : str
        The output value.
    """
    github_output = os.environ["GITHUB_OUTPUT"]
    with Path(github_output).open("a", encoding="utf-8") as file:
        file.write(f"{name}={value}\n")


def find_latest_release_tag() -> tuple[int, int, int]:
    """Fetch tags and return the ``(major, minor, patch)`` of the latest release.

    Returns
    -------
    tuple[int, int, int]
        The ``(major, minor, patch)`` of the latest ``vX.Y.Z`` tag.
    """
    log_progress("Fetching tags to find the latest release.")
    run_git("fetch", "--tags")
    output = run_git("tag", "--list", "v*", "--sort=-version:refname")
    version = parse_latest_release_tag(output.splitlines())
    log_progress(f"Latest release tag: v{version[0]}.{version[1]}.{version[2]}.")
    return version


def merge_main_into_release(main_branch: str, version_location: str) -> None:
    """Merge ``main_branch`` into the current branch, auto-resolving version/lock conflicts.

    Parameters
    ----------
    main_branch : str
        Name of the branch to merge into the current branch.
    version_location : str
        Path to the version file; conflicting hunks in it (and in lock files) are resolved
        by keeping the current branch's side.
    """
    log_progress(f"Merging '{main_branch}' into the release branch.")
    result = subprocess.run(
        ["git", "merge", main_branch, "--no-edit"], capture_output=True, text=True
    )
    if result.returncode == 0:
        return

    conflicted = run_git("diff", "--name-only", "--diff-filter=U").splitlines()
    if classify_merge_conflict(conflicted, version_location):
        for path in conflicted:
            keep_ours_in_conflicts(path)
        run_git("commit", "--no-edit")
        return

    log_progress("Aborting merge because conflicts could not be automatically resolved.")
    run_git("merge", "--abort", check=False)
    raise AutoReleaseError(
        "Merge conflicts detected outside of the version file: "
        f"{', '.join(conflicted) or 'unknown'}. Please resolve manually.\n"
        f"git merge output:\n{result.stdout}\n{result.stderr}"
    )


def cherry_pick_commits_into_release(commits: list[str], version_location: str) -> None:
    """Cherry-pick each of ``commits`` onto the current branch, in order.

    Auto-resolves conflicts the same way ``merge_main_into_release`` does, if they're limited
    to the version file and/or lock files; skips commits emptied by that resolution and
    aborts with a clear error for other conflicts.

    Parameters
    ----------
    commits : list[str]
        Commit SHAs to cherry-pick, in order.
    version_location : str
        Path to the version file; conflicting hunks in it (and in lock files) are resolved
        by keeping the current branch's side.
    """
    for commit in commits:
        log_progress(f"Cherry-picking commit '{commit}'.")
        result = subprocess.run(["git", "cherry-pick", commit], capture_output=True, text=True)
        if result.returncode == 0:
            continue

        conflicted = run_git("diff", "--name-only", "--diff-filter=U").splitlines()
        if classify_merge_conflict(conflicted, version_location):
            for path in conflicted:
                keep_ours_in_conflicts(path)
            if run_git("diff", "--cached", "--name-only"):
                # `cherry-pick --continue` would open an editor in non-interactive CI.
                run_git("commit", "--no-edit")
            else:
                log_progress(
                    f"Skipping commit '{commit}': no changes remain after conflict resolution."
                )
                run_git("cherry-pick", "--skip")
            continue

        log_progress(
            f"Aborting cherry-pick of '{commit}' because conflicts require manual resolution."
        )
        run_git("cherry-pick", "--abort", check=False)
        raise AutoReleaseError(
            f"Cherry-pick of commit '{commit}' produced conflicts outside of the version "
            f"file: {', '.join(conflicted) or 'unknown'}. Please resolve manually.\n"
            f"git cherry-pick output:\n{result.stdout}\n{result.stderr}"
        )


def run_minor_major_release(
    release_type: str,
    version_source: str,
    version_location: str,
    main_branch: str,
    branch_prefix: str,
    lock_file_tool: str,
) -> tuple[str, str, str, str]:
    """Perform a minor or major release.

    Parameters
    ----------
    release_type : str
        Either ``"minor"`` or ``"major"``.
    version_source : str
        Where the version is stored (``file``, ``pyproject``, ``setup-py``, or
        ``python-module``).
    version_location : str
        Path to the file identified by ``version_source``.
    main_branch : str
        Name of the main development branch.
    branch_prefix : str
        Prefix used to compute the release branch name.
    lock_file_tool : str
        Which lock file tooling to regenerate with after each version bump: ``none``, ``uv``,
        or ``poetry``.

    Returns
    -------
    tuple[str, str, str, str]
        ``(release_version, dev_version, branch, dev_version_pr_url)``.
    """
    log_progress(f"Synchronizing main branch '{main_branch}'.")
    run_git("checkout", main_branch)
    run_git("pull")

    current_dev_version = read_version(version_source, version_location)
    log_progress(f"Current version in '{version_location}': {current_dev_version}.")
    require_dev_version(current_dev_version, main_branch)
    release_version, dev_version, branch = bump_minor_major(
        current_dev_version, release_type, branch_prefix
    )
    log_progress(f"Target release: v{release_version}; next development version: {dev_version}.")
    bump_branch = f"chore/bump-dev-version-v{dev_version}"
    require_refs_available(
        f"refs/heads/{branch}", f"refs/tags/v{release_version}", f"refs/heads/{bump_branch}"
    )

    with rollback_on_failure() as journal:
        log_progress(f"Creating release branch '{branch}'.")
        run_git("checkout", "-b", branch)
        log_progress(f"Writing release version {release_version} to '{version_location}'.")
        write_version(version_source, version_location, release_version)
        lock_file = update_lock_file(lock_file_tool, version_location)
        run_git("add", version_location)
        if lock_file:
            run_git("add", lock_file)
        run_git("commit", "-m", f"release: v{release_version}")
        run_git("tag", f"v{release_version}", branch)
        journal.record_local_tag(f"v{release_version}")
        log_progress(f"Pushing release branch '{branch}'.")
        journal.push_branch(branch)

        log_progress(f"Preparing development-version bump on '{bump_branch}'.")
        run_git("checkout", main_branch)
        run_git("checkout", "-b", bump_branch)
        log_progress(f"Writing development version {dev_version} to '{version_location}'.")
        write_version(version_source, version_location, dev_version)
        lock_file = update_lock_file(lock_file_tool, version_location)
        run_git("add", version_location)
        if lock_file:
            run_git("add", lock_file)
        run_git("commit", "-m", dev_version_bump_pr_title(dev_version))
        log_progress(f"Pushing development-version branch '{bump_branch}'.")
        journal.push_branch(bump_branch)
        log_progress("Creating draft development-version pull request.")
        dev_version_pr_url = create_dev_version_bump_pr(
            main_branch, bump_branch, release_version, dev_version
        )
        journal.record_pull_request(dev_version_pr_url)
        log_progress(f"Draft development-version pull request created: {dev_version_pr_url}")

        # The tag is the final remote write; removing it cannot undo triggered workflows.
        log_progress(f"Pushing tag 'v{release_version}'.")
        journal.push_tag(f"v{release_version}")

    return release_version, dev_version, branch, dev_version_pr_url


def _finish_patch_release(
    version_source: str,
    version_location: str,
    main_branch: str,
    branch_prefix: str,
    lock_file_tool: str,
    apply_changes: Callable[[], None],
) -> tuple[str, str]:
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
    lock_file_tool : str
        Which lock file tooling to regenerate with after the version bump: ``none``, ``uv``,
        or ``poetry``.
    apply_changes : Callable[[], None]
        Called with the release branch checked out, to bring in the desired changes (merge
        all of main, or cherry-pick specific commits) before the version is bumped.

    Returns
    -------
    tuple[str, str]
        ``(release_version, release_branch)``.
    """
    log_progress(f"Synchronizing main branch '{main_branch}'.")
    run_git("checkout", main_branch)
    run_git("pull")

    major, minor, _patch = find_latest_release_tag()
    branch = release_branch_name(branch_prefix, major, minor)

    log_progress(f"Checking out release branch '{branch}'.")
    run_git("checkout", branch)
    apply_changes()

    current_version = read_version(version_source, version_location)
    release_version = bump_patch(current_version)
    log_progress(
        f"Current version in '{version_location}': {current_version}; "
        f"target release: v{release_version}."
    )
    require_refs_available(f"refs/tags/v{release_version}")
    log_progress(f"Writing release version {release_version} to '{version_location}'.")
    write_version(version_source, version_location, release_version)
    lock_file = update_lock_file(lock_file_tool, version_location)
    run_git("add", version_location)
    if lock_file:
        run_git("add", lock_file)
    run_git("commit", "-m", f"release: v{release_version}")
    log_progress(f"Returning to main branch '{main_branch}'.")
    run_git("checkout", main_branch)
    with rollback_on_failure() as journal:
        run_git("tag", f"v{release_version}", branch)
        journal.record_local_tag(f"v{release_version}")
        log_progress(f"Pushing release branch '{branch}'.")
        journal.push_branch(branch)
        log_progress(f"Pushing tag 'v{release_version}'.")
        journal.push_tag(f"v{release_version}")

    return release_version, branch


def run_patch_release(
    version_source: str,
    version_location: str,
    main_branch: str,
    branch_prefix: str,
    lock_file_tool: str,
) -> tuple[str, str]:
    """Perform a patch release by merging all of main into the release branch.

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
    lock_file_tool : str
        Which lock file tooling to regenerate with after the version bump: ``none``, ``uv``,
        or ``poetry``.

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
        lock_file_tool,
        lambda: merge_main_into_release(main_branch, version_location),
    )


def run_patch_cherry_pick_release(
    version_source: str,
    version_location: str,
    main_branch: str,
    branch_prefix: str,
    lock_file_tool: str,
    commits: list[str],
) -> tuple[str, str]:
    """Perform a patch release by cherry-picking specific commits onto the release branch.

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
    lock_file_tool : str
        Which lock file tooling to regenerate with after the version bump: ``none``, ``uv``,
        or ``poetry``.
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
        lock_file_tool,
        lambda: cherry_pick_commits_into_release(commits, version_location),
    )


def require_env(name: str) -> str:
    """Return the value of environment variable ``name``, or raise ``AutoReleaseError``.

    Parameters
    ----------
    name : str
        The environment variable name.

    Returns
    -------
    str
        The environment variable's value.
    """
    try:
        return os.environ[name]
    except KeyError:
        raise AutoReleaseError(f"Missing required environment variable '{name}'.") from None


def main() -> None:
    """Entry point: read inputs from the environment and perform the release."""
    valid_release_types = ("patch", "patch-cherry-pick", "minor", "major")
    valid_version_sources = ("file", "pyproject", "setup-py", "python-module")
    valid_lock_file_tools = ("none", "uv", "poetry")

    release_type = require_env("RELEASE_TYPE")
    version_source = require_env("VERSION_SOURCE")
    version_location = require_env("VERSION_LOCATION")
    main_branch = require_env("MAIN_BRANCH")
    branch_prefix = require_env("RELEASE_BRANCH_PREFIX")
    lock_file_tool = require_env("LOCK_FILE_TOOL")

    if release_type not in valid_release_types:
        raise AutoReleaseError(
            f"Invalid release-type '{release_type}'. Must be one of {valid_release_types}."
        )
    if version_source not in valid_version_sources:
        raise AutoReleaseError(
            f"Invalid version-source '{version_source}'. Must be one of {valid_version_sources}."
        )
    if lock_file_tool not in valid_lock_file_tools:
        raise AutoReleaseError(
            f"Invalid lock-file-tool '{lock_file_tool}'. Must be one of {valid_lock_file_tools}."
        )

    log_progress(
        f"Starting {release_type} release "
        f"(version-source: {version_source}, version-location: '{version_location}')."
    )

    if release_type == "patch":
        release_version, branch = run_patch_release(
            version_source, version_location, main_branch, branch_prefix, lock_file_tool
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
            version_source, version_location, main_branch, branch_prefix, lock_file_tool, commits
        )
        dev_version = ""
        dev_version_pr_url = ""
    else:
        release_version, dev_version, branch, dev_version_pr_url = run_minor_major_release(
            release_type,
            version_source,
            version_location,
            main_branch,
            branch_prefix,
            lock_file_tool,
        )

    export_output("new-version", release_version)
    export_output("new-dev-version", dev_version)
    export_output("release-branch", branch)
    export_output("dev-version-pr-url", dev_version_pr_url)
    log_progress(f"Release complete: v{release_version} on '{branch}'. Action outputs exported.")


if __name__ == "__main__":
    try:
        main()
    except AutoReleaseError as error:
        print(f"::error::{error}", file=sys.stderr, flush=True)
        sys.exit(1)
