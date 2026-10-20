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
    run_patch_cherry_pick_release,
    run_patch_release,
    write_version,
)
import pytest
import tomlkit

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


def _fake_update_lock_file(calls, lock_file_name="fake.lock", content="fake-lock-content\n"):
    """Return a stand-in for update_lock_file that records its arg and writes a fake lock file."""

    def _fake(lock_file_tool, version_location):
        calls.append(lock_file_tool)
        Path(lock_file_name).write_text(content)
        return lock_file_name

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
        "minor", git_repo.version_source, git_repo.version_location, "main", "release/", "none"
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
            "minor",
            git_repo.version_source,
            git_repo.version_location,
            "main",
            "release/",
            "none",
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
            "minor",
            git_repo.version_source,
            git_repo.version_location,
            "main",
            "release/",
            "none",
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
            "minor",
            git_repo.version_source,
            git_repo.version_location,
            "main",
            "release/",
            "none",
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
        "minor", git_repo.version_source, git_repo.version_location, "main", "release/", "none"
    )

    release_version, branch = run_patch_release(
        git_repo.version_source, git_repo.version_location, "main", "release/", "none"
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
        "minor", git_repo.version_source, git_repo.version_location, "main", "release/", "none"
    )

    # Diverge main's version further so merging it would otherwise conflict.
    _run("checkout", "main", cwd=git_repo.path)
    write_version(git_repo.version_source, git_repo.version_location, "0.3.dev1")
    _run("commit", "-am", "chore: tweak dev version", cwd=git_repo.path)
    _run("push", "origin", "main", cwd=git_repo.path)

    release_version, branch = run_patch_release(
        git_repo.version_source, git_repo.version_location, "main", "release/", "none"
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
        "minor", git_repo.version_source, git_repo.version_location, "main", "release/", "none"
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
        run_patch_release(
            git_repo.version_source, git_repo.version_location, "main", "release/", "none"
        )

    # These can only be present because of the appended `git merge` stdout/stderr:
    # "git merge output:" is our literal label, and "CONFLICT (" is text git itself
    # emits on stdout when a merge conflict occurs.
    message = str(exc_info.value)
    assert "git merge output:" in message
    assert "CONFLICT (" in message

    # The merge must have been aborted, leaving a clean working tree.
    assert _run("status", "--porcelain", cwd=git_repo.path) == ""


def test_run_patch_cherry_pick_release_only_picks_listed_commits(git_repo, monkeypatch):
    """Test that patch-cherry-pick only brings in the listed commits, not all of main."""
    calls = []
    monkeypatch.setattr(
        "autorelease.create_dev_version_bump_pr", _fake_create_dev_version_bump_pr(calls)
    )
    run_minor_major_release(
        "minor", git_repo.version_source, git_repo.version_location, "main", "release/", "none"
    )

    _run("checkout", "main", cwd=git_repo.path)
    (git_repo.path / "a.txt").write_text("a\n")
    _run("add", "a.txt", cwd=git_repo.path)
    _run("commit", "-m", "feat: add a", cwd=git_repo.path)
    commit_a = _run("rev-parse", "HEAD", cwd=git_repo.path)

    (git_repo.path / "b.txt").write_text("b\n")
    _run("add", "b.txt", cwd=git_repo.path)
    _run("commit", "-m", "feat: add b (should NOT be cherry-picked)", cwd=git_repo.path)

    (git_repo.path / "c.txt").write_text("c\n")
    _run("add", "c.txt", cwd=git_repo.path)
    _run("commit", "-m", "feat: add c", cwd=git_repo.path)
    commit_c = _run("rev-parse", "HEAD", cwd=git_repo.path)
    _run("push", "origin", "main", cwd=git_repo.path)

    release_version, branch = run_patch_cherry_pick_release(
        git_repo.version_source,
        git_repo.version_location,
        "main",
        "release/",
        "none",
        [commit_a, commit_c],
    )

    assert release_version == "0.2.1"
    _run("checkout", branch, cwd=git_repo.path)
    assert (git_repo.path / "a.txt").exists()
    assert not (git_repo.path / "b.txt").exists()
    assert (git_repo.path / "c.txt").exists()
    assert read_version(git_repo.version_source, git_repo.version_location) == "0.2.1"


def test_run_patch_cherry_pick_release_aborts_on_unrelated_conflict(git_repo, monkeypatch):
    """Test that patch-cherry-pick aborts the cherry-pick when an unrelated file conflicts."""
    calls = []
    monkeypatch.setattr(
        "autorelease.create_dev_version_bump_pr", _fake_create_dev_version_bump_pr(calls)
    )
    run_minor_major_release(
        "minor", git_repo.version_source, git_repo.version_location, "main", "release/", "none"
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
    commit = _run("rev-parse", "HEAD", cwd=git_repo.path)
    _run("push", "origin", "main", cwd=git_repo.path)

    with pytest.raises(AutoReleaseError, match="produced conflicts"):
        run_patch_cherry_pick_release(
            git_repo.version_source,
            git_repo.version_location,
            "main",
            "release/",
            "none",
            [commit],
        )

    assert _run("status", "--porcelain", cwd=git_repo.path) == ""


def test_run_patch_release_rejects_if_tag_already_exists(git_repo, monkeypatch):
    """Test that a (merge-all) patch release refuses to run if the release tag already exists."""
    calls = []
    monkeypatch.setattr(
        "autorelease.create_dev_version_bump_pr", _fake_create_dev_version_bump_pr(calls)
    )
    run_minor_major_release(
        "minor", git_repo.version_source, git_repo.version_location, "main", "release/", "none"
    )
    _run("tag", "v0.2.1", cwd=git_repo.path)
    _run("push", "origin", "v0.2.1", cwd=git_repo.path)
    # Delete the local tag so only 'origin' carries the leftover ref (see comment in the
    # release-branch variant of this test, above) -- otherwise the plain `git tag` command
    # inside run_patch_release would itself fail locally with its own "already exists"
    # message, which would also match this test's pattern and mask whether
    # require_refs_available actually ran.
    _run("tag", "-d", "v0.2.1", cwd=git_repo.path)

    with pytest.raises(AutoReleaseError, match="already exist"):
        run_patch_release(
            git_repo.version_source, git_repo.version_location, "main", "release/", "none"
        )

    # The release branch must never have received the bump commit/push.
    _run("checkout", "release/0.2", cwd=git_repo.path)
    assert read_version(git_repo.version_source, git_repo.version_location) == "0.2.0"


def test_run_minor_major_release_regenerates_lock_file(git_repo, monkeypatch):
    """Test that a minor/major release regenerates and commits the lock file on both bumps."""
    pr_calls = []
    monkeypatch.setattr(
        "autorelease.create_dev_version_bump_pr", _fake_create_dev_version_bump_pr(pr_calls)
    )
    lock_calls = []
    monkeypatch.setattr("autorelease.update_lock_file", _fake_update_lock_file(lock_calls))

    release_version, dev_version, branch, pr_url = run_minor_major_release(
        "minor", git_repo.version_source, git_repo.version_location, "main", "release/", "uv"
    )

    # update_lock_file must be called once for the release-branch bump, once for the
    # main-branch dev-version bump.
    assert lock_calls == ["uv", "uv"]

    _run("checkout", branch, cwd=git_repo.path)
    assert _run("ls-files", "fake.lock", cwd=git_repo.path) == "fake.lock"
    assert (git_repo.path / "fake.lock").read_text() == "fake-lock-content\n"

    _run("checkout", "chore/bump-dev-version-v0.3.dev0", cwd=git_repo.path)
    assert _run("ls-files", "fake.lock", cwd=git_repo.path) == "fake.lock"
    assert (git_repo.path / "fake.lock").read_text() == "fake-lock-content\n"


def test_run_patch_release_regenerates_lock_file(git_repo, monkeypatch):
    """Test that a patch release regenerates and commits the lock file."""
    pr_calls = []
    monkeypatch.setattr(
        "autorelease.create_dev_version_bump_pr", _fake_create_dev_version_bump_pr(pr_calls)
    )
    lock_calls = []
    monkeypatch.setattr("autorelease.update_lock_file", _fake_update_lock_file(lock_calls))
    run_minor_major_release(
        "minor", git_repo.version_source, git_repo.version_location, "main", "release/", "none"
    )
    lock_calls.clear()

    release_version, branch = run_patch_release(
        git_repo.version_source, git_repo.version_location, "main", "release/", "poetry"
    )

    assert lock_calls == ["poetry"]
    _run("checkout", branch, cwd=git_repo.path)
    assert _run("ls-files", "fake.lock", cwd=git_repo.path) == "fake.lock"
    assert (git_repo.path / "fake.lock").read_text() == "fake-lock-content\n"


def _fake_uv_lock(lock_file_tool, version_location):
    """Stand-in for update_lock_file that writes a uv.lock embedding the project's version."""
    project = tomlkit.parse(Path(version_location).read_text())["project"]
    Path("uv.lock").write_text(
        f'version = "{project["version"]}"\n'
        "# separates the version and dependencies hunks\n"
        f'dependencies = "{",".join(project["dependencies"])}"\n'
    )
    return "uv.lock"


def _setup_uv_project_with_diverged_main(git_repo, monkeypatch):
    """Cut release/0.2, then land the dev-version bump and a new dependency on main.

    Returns the ``(dev_bump_commit, dependency_commit)`` SHAs on main.
    """
    monkeypatch.setattr(
        "autorelease.create_dev_version_bump_pr", _fake_create_dev_version_bump_pr([])
    )
    monkeypatch.setattr("autorelease.update_lock_file", _fake_uv_lock)

    pyproject = git_repo.path / "pyproject.toml"
    pyproject.write_text(
        '[project]\nname = "demo"\nversion = "0.2.dev0"\ndescription = "demo"\ndependencies = []\n'
    )
    _fake_uv_lock("uv", "pyproject.toml")
    _run("add", "pyproject.toml", "uv.lock", cwd=git_repo.path)
    _run("commit", "-m", "chore: add uv.lock", cwd=git_repo.path)
    _run("push", "origin", "main", cwd=git_repo.path)

    run_minor_major_release("minor", "pyproject", "pyproject.toml", "main", "release/", "uv")

    _run("checkout", "main", cwd=git_repo.path)
    _run("merge", "--ff-only", "chore/bump-dev-version-v0.3.dev0", cwd=git_repo.path)
    dev_bump_commit = _run("rev-parse", "HEAD", cwd=git_repo.path)
    pyproject.write_text(pyproject.read_text().replace("[]", '["requests"]'))
    _fake_uv_lock("uv", "pyproject.toml")
    _run("commit", "-am", "feat: add requests", cwd=git_repo.path)
    dependency_commit = _run("rev-parse", "HEAD", cwd=git_repo.path)
    _run("push", "origin", "main", cwd=git_repo.path)
    return dev_bump_commit, dependency_commit


def _assert_release_keeps_version_and_gets_dependency(git_repo, branch):
    _run("checkout", branch, cwd=git_repo.path)
    assert read_version("pyproject", "pyproject.toml") == "0.2.1"
    assert '["requests"]' in (git_repo.path / "pyproject.toml").read_text()
    assert (git_repo.path / "uv.lock").read_text() == (
        'version = "0.2.1"\n'
        "# separates the version and dependencies hunks\n"
        'dependencies = "requests"\n'
    )


@pytest.mark.parametrize("git_repo", ["pyproject"], indirect=True)
def test_run_patch_release_auto_resolves_pyproject_and_lock_file_conflict(git_repo, monkeypatch):
    """Test that a patch release keeps the release side of conflicting pyproject/lock hunks."""
    _setup_uv_project_with_diverged_main(git_repo, monkeypatch)

    release_version, branch = run_patch_release(
        "pyproject", "pyproject.toml", "main", "release/", "uv"
    )

    assert release_version == "0.2.1"
    _assert_release_keeps_version_and_gets_dependency(git_repo, branch)


@pytest.mark.parametrize("git_repo", ["pyproject"], indirect=True)
def test_run_patch_cherry_pick_release_auto_resolves_pyproject_and_lock_file_conflict(
    git_repo, monkeypatch
):
    """Test that patch-cherry-pick keeps the release side of conflicting pyproject/lock hunks."""
    commits = _setup_uv_project_with_diverged_main(git_repo, monkeypatch)

    release_version, branch = run_patch_cherry_pick_release(
        "pyproject", "pyproject.toml", "main", "release/", "uv", list(commits)
    )

    assert release_version == "0.2.1"
    _assert_release_keeps_version_and_gets_dependency(git_repo, branch)
