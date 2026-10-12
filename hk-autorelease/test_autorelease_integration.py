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

import subprocess

import pytest

from autorelease import AutoReleaseError, run_minor_major_release, run_patch_release


def _run(*args, cwd):
    result = subprocess.run(["git", *args], cwd=cwd, capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    return result.stdout.strip()


@pytest.fixture
def git_repo(tmp_path, monkeypatch):
    """Create a bare 'origin' repo and a clone with an initial VERSION file on main."""
    origin = tmp_path / "origin.git"
    work = tmp_path / "work"
    _run("init", "--bare", "--initial-branch=main", str(origin), cwd=tmp_path)
    _run("clone", str(origin), str(work), cwd=tmp_path)
    _run("config", "user.email", "bot@example.com", cwd=work)
    _run("config", "user.name", "bot", cwd=work)

    (work / "VERSION").write_text("0.2.dev0\n")
    _run("add", "VERSION", cwd=work)
    _run("commit", "-m", "chore: initial version", cwd=work)
    _run("push", "origin", "main", cwd=work)

    monkeypatch.chdir(work)
    return work


def test_run_minor_major_release_minor(git_repo):
    release_version, dev_version, branch = run_minor_major_release(
        "minor", "file", "VERSION", "main", "release/"
    )

    assert release_version == "0.2.0"
    assert dev_version == "0.3.dev0"
    assert branch == "release/0.2"
    assert (git_repo / "VERSION").read_text() == "0.3.dev0\n"
    assert _run("tag", "--list", "v0.2.0", cwd=git_repo) == "v0.2.0"

    _run("checkout", branch, cwd=git_repo)
    assert (git_repo / "VERSION").read_text() == "0.2.0\n"


def test_run_patch_release_clean_merge(git_repo):
    run_minor_major_release("minor", "file", "VERSION", "main", "release/")

    release_version, branch = run_patch_release("file", "VERSION", "main", "release/")

    assert release_version == "0.2.1"
    assert branch == "release/0.2"
    assert _run("tag", "--list", "v0.2.1", cwd=git_repo) == "v0.2.1"
    _run("checkout", branch, cwd=git_repo)
    assert (git_repo / "VERSION").read_text() == "0.2.1\n"


def test_run_patch_release_auto_resolves_version_only_conflict(git_repo):
    run_minor_major_release("minor", "file", "VERSION", "main", "release/")

    # Diverge main's VERSION further so merging it would otherwise conflict.
    _run("checkout", "main", cwd=git_repo)
    (git_repo / "VERSION").write_text("0.3.dev1\n")
    _run("commit", "-am", "chore: tweak dev version", cwd=git_repo)
    _run("push", "origin", "main", cwd=git_repo)

    release_version, branch = run_patch_release("file", "VERSION", "main", "release/")

    assert release_version == "0.2.1"
    _run("checkout", branch, cwd=git_repo)
    assert (git_repo / "VERSION").read_text() == "0.2.1\n"


def test_run_patch_release_aborts_on_unrelated_conflict(git_repo):
    run_minor_major_release("minor", "file", "VERSION", "main", "release/")

    _run("checkout", "release/0.2", cwd=git_repo)
    (git_repo / "README.md").write_text("release branch content\n")
    _run("add", "README.md", cwd=git_repo)
    _run("commit", "-m", "docs: release branch readme", cwd=git_repo)
    _run("push", "origin", "release/0.2", cwd=git_repo)

    _run("checkout", "main", cwd=git_repo)
    (git_repo / "README.md").write_text("main branch content\n")
    _run("add", "README.md", cwd=git_repo)
    _run("commit", "-m", "docs: main readme", cwd=git_repo)
    _run("push", "origin", "main", cwd=git_repo)

    with pytest.raises(AutoReleaseError, match="Merge conflicts detected"):
        run_patch_release("file", "VERSION", "main", "release/")

    # The merge must have been aborted, leaving a clean working tree.
    assert _run("status", "--porcelain", cwd=git_repo) == ""
