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

"""Integration tests for hk-autorelease git orchestration, using real temp git repos."""

from pathlib import Path
import subprocess
from typing import NamedTuple

from autorelease import (
    AutoReleaseError,
    read_version,
    run_minor_major_release,
    run_patch_release,
    write_version,
)
import pytest

# Starting content for each version-source kind, seeded with version "0.2.dev0".
VERSION_SOURCE_CASES = {
    "file": ("VERSION", "0.2.dev0\n"),
    "pyproject": ("pyproject.toml", '[project]\nname = "demo"\nversion = "0.2.dev0"\n'),
    "setup-py": (
        "setup.py",
        "from setuptools import setup\n\nsetup(\n    name='demo',\n    version='0.2.dev0',\n)\n",
    ),
    "python-module": ("_version.py", '__version__ = "0.2.dev0"\n'),
}


class GitRepo(NamedTuple):
    """A working-tree git repo plus the version-source config used to seed it."""

    path: Path
    version_source: str
    version_location: str


def _run(*args, cwd):
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


def _fake_create_dev_version_bump_pr(calls):
    """Return a stand-in for create_dev_version_bump_pr that records its call args."""

    def _fake(main_branch, bump_branch, release_version, dev_version):
        calls.append((main_branch, bump_branch, release_version, dev_version))
        return "https://example.invalid/pr/1"

    return _fake


@pytest.fixture(params=sorted(VERSION_SOURCE_CASES))
def git_repo(tmp_path, monkeypatch, request):
    """Create a bare 'origin' repo and a clone with an initial version on main.

    Parametrized across all four ``version-source`` kinds, so every test using
    this fixture runs once per kind.
    """
    version_source = request.param
    version_location, initial_content = VERSION_SOURCE_CASES[version_source]

    origin = tmp_path / "origin.git"
    work = tmp_path / "work"
    _run("init", "--bare", "--initial-branch=main", str(origin), cwd=tmp_path)
    _run("clone", str(origin), str(work), cwd=tmp_path)
    _run("config", "user.email", "bot@example.com", cwd=work)
    _run("config", "user.name", "bot", cwd=work)

    (work / version_location).write_text(initial_content)
    _run("add", version_location, cwd=work)
    _run("commit", "-m", "chore: initial version", cwd=work)
    _run("push", "origin", "main", cwd=work)

    monkeypatch.chdir(work)
    return GitRepo(path=work, version_source=version_source, version_location=version_location)


def test_run_minor_major_release_minor(git_repo, monkeypatch):
    """Test a minor release: tags the release branch, opens a draft dev-version-bump PR."""
    calls = []
    monkeypatch.setattr(
        "autorelease.create_dev_version_bump_pr", _fake_create_dev_version_bump_pr(calls)
    )

    release_version, dev_version, branch, pr_url = run_minor_major_release(
        "minor", git_repo.version_source, git_repo.version_location, "main", "release/"
    )

    assert release_version == "0.2.0"
    assert dev_version == "0.3.dev0"
    assert branch == "release/0.2"
    assert pr_url == "https://example.invalid/pr/1"
    assert calls == [("main", "chore/bump-dev-version-v0.3.dev0", "0.2.0", "0.3.dev0")]

    _run("tag", "--list", "v0.2.0", cwd=git_repo.path)
    assert _run("tag", "--list", "v0.2.0", cwd=git_repo.path) == "v0.2.0"

    # main itself must be untouched: still the original dev version.
    _run("checkout", "main", cwd=git_repo.path)
    assert read_version(git_repo.version_source, git_repo.version_location) == "0.2.dev0"

    # the bump branch carries the new dev version.
    _run("checkout", "chore/bump-dev-version-v0.3.dev0", cwd=git_repo.path)
    assert read_version(git_repo.version_source, git_repo.version_location) == "0.3.dev0"

    _run("checkout", branch, cwd=git_repo.path)
    assert read_version(git_repo.version_source, git_repo.version_location) == "0.2.0"


def test_run_minor_major_release_rejects_non_dev_version(git_repo, monkeypatch):
    """Test that a minor/major release refuses to run if main doesn't hold a dev version."""
    calls = []
    monkeypatch.setattr(
        "autorelease.create_dev_version_bump_pr", _fake_create_dev_version_bump_pr(calls)
    )
    write_version(git_repo.version_source, git_repo.version_location, "0.2.0")
    _run("commit", "-am", "chore: not a dev version", cwd=git_repo.path)
    _run("push", "origin", "main", cwd=git_repo.path)

    with pytest.raises(AutoReleaseError, match="Expected a development version"):
        run_minor_major_release(
            "minor", git_repo.version_source, git_repo.version_location, "main", "release/"
        )

    assert calls == []


def test_run_minor_major_release_rejects_if_release_branch_already_exists(git_repo, monkeypatch):
    """Test that a minor/major release refuses to run if the release branch already exists."""
    calls = []
    monkeypatch.setattr(
        "autorelease.create_dev_version_bump_pr", _fake_create_dev_version_bump_pr(calls)
    )
    _run("checkout", "-b", "release/0.2", cwd=git_repo.path)
    _run("push", "origin", "release/0.2", cwd=git_repo.path)
    _run("checkout", "main", cwd=git_repo.path)
    # Delete the local branch so only 'origin' carries the leftover ref, as it would after a
    # partially-failed run on a fresh checkout -- otherwise git's own local-branch-exists error
    # would mask whether the new pre-flight guard actually fired.
    _run("branch", "-D", "release/0.2", cwd=git_repo.path)
    remote_ref_before = _run("ls-remote", "origin", "refs/heads/release/0.2", cwd=git_repo.path)

    with pytest.raises(AutoReleaseError, match="already exist"):
        run_minor_major_release(
            "minor", git_repo.version_source, git_repo.version_location, "main", "release/"
        )

    assert calls == []
    # main must be untouched.
    assert read_version(git_repo.version_source, git_repo.version_location) == "0.2.dev0"
    # the release branch on origin must be unchanged (never re-pushed with a new commit).
    assert (
        _run("ls-remote", "origin", "refs/heads/release/0.2", cwd=git_repo.path)
        == remote_ref_before
    )


def test_run_minor_major_release_rejects_if_tag_already_exists(git_repo, monkeypatch):
    """Test that a minor/major release refuses to run if the release tag already exists."""
    calls = []
    monkeypatch.setattr(
        "autorelease.create_dev_version_bump_pr", _fake_create_dev_version_bump_pr(calls)
    )
    _run("tag", "v0.2.0", cwd=git_repo.path)
    _run("push", "origin", "v0.2.0", cwd=git_repo.path)
    # Delete the local tag so only 'origin' carries the leftover ref (see comment in the
    # release-branch variant of this test, above).
    _run("tag", "-d", "v0.2.0", cwd=git_repo.path)

    with pytest.raises(AutoReleaseError, match="already exist"):
        run_minor_major_release(
            "minor", git_repo.version_source, git_repo.version_location, "main", "release/"
        )

    assert calls == []
    # the release branch must never have been pushed.
    assert _run("ls-remote", "origin", "refs/heads/release/0.2", cwd=git_repo.path) == ""


def test_run_patch_release_clean_merge(git_repo, monkeypatch):
    """Test a patch release that merges cleanly into the existing release branch."""
    calls = []
    monkeypatch.setattr(
        "autorelease.create_dev_version_bump_pr", _fake_create_dev_version_bump_pr(calls)
    )
    run_minor_major_release(
        "minor", git_repo.version_source, git_repo.version_location, "main", "release/"
    )

    release_version, branch = run_patch_release(
        git_repo.version_source, git_repo.version_location, "main", "release/"
    )

    assert release_version == "0.2.1"
    assert branch == "release/0.2"
    assert _run("tag", "--list", "v0.2.1", cwd=git_repo.path) == "v0.2.1"
    _run("checkout", branch, cwd=git_repo.path)
    assert read_version(git_repo.version_source, git_repo.version_location) == "0.2.1"


def test_run_patch_release_auto_resolves_version_only_conflict(git_repo, monkeypatch):
    """Test that a patch release auto-resolves a merge conflict limited to the version file."""
    calls = []
    monkeypatch.setattr(
        "autorelease.create_dev_version_bump_pr", _fake_create_dev_version_bump_pr(calls)
    )
    run_minor_major_release(
        "minor", git_repo.version_source, git_repo.version_location, "main", "release/"
    )

    # Diverge main's version further so merging it would otherwise conflict.
    _run("checkout", "main", cwd=git_repo.path)
    write_version(git_repo.version_source, git_repo.version_location, "0.3.dev1")
    _run("commit", "-am", "chore: tweak dev version", cwd=git_repo.path)
    _run("push", "origin", "main", cwd=git_repo.path)

    release_version, branch = run_patch_release(
        git_repo.version_source, git_repo.version_location, "main", "release/"
    )

    assert release_version == "0.2.1"
    _run("checkout", branch, cwd=git_repo.path)
    assert read_version(git_repo.version_source, git_repo.version_location) == "0.2.1"


def test_run_patch_release_aborts_on_unrelated_conflict(git_repo, monkeypatch):
    """Test that a patch release aborts the merge when an unrelated file conflicts."""
    calls = []
    monkeypatch.setattr(
        "autorelease.create_dev_version_bump_pr", _fake_create_dev_version_bump_pr(calls)
    )
    run_minor_major_release(
        "minor", git_repo.version_source, git_repo.version_location, "main", "release/"
    )

    _run("checkout", "release/0.2", cwd=git_repo.path)
    (git_repo.path / "README.md").write_text("release branch content\n")
    _run("add", "README.md", cwd=git_repo.path)
    _run("commit", "-m", "docs: release branch readme", cwd=git_repo.path)
    _run("push", "origin", "release/0.2", cwd=git_repo.path)

    _run("checkout", "main", cwd=git_repo.path)
    (git_repo.path / "README.md").write_text("main branch content\n")
    _run("add", "README.md", cwd=git_repo.path)
    _run("commit", "-m", "docs: main readme", cwd=git_repo.path)
    _run("push", "origin", "main", cwd=git_repo.path)

    with pytest.raises(AutoReleaseError, match="Merge conflicts detected") as exc_info:
        run_patch_release(git_repo.version_source, git_repo.version_location, "main", "release/")

    # These can only be present because of the appended `git merge` stdout/stderr:
    # "git merge output:" is our literal label, and "CONFLICT (" is text git itself
    # emits on stdout when a merge conflict occurs.
    message = str(exc_info.value)
    assert "git merge output:" in message
    assert "CONFLICT (" in message

    # The merge must have been aborted, leaving a clean working tree.
    assert _run("status", "--porcelain", cwd=git_repo.path) == ""
