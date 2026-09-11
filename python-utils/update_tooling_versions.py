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
"""Update pinned versions for the maintenance tooling refresh workflow."""

from __future__ import annotations

import argparse
from datetime import UTC, datetime
import hashlib
import json
import os
from pathlib import Path
import re
import subprocess
import tempfile
from typing import Any

ONE_WEEK_SECONDS = 7 * 24 * 60 * 60


def _now_utc() -> datetime:
    """Return the current UTC time."""
    return datetime.now(UTC)


def select_release_older_than(releases: list[dict[str, Any]], age_seconds: int) -> str | None:
    """Return the newest eligible tag older than the threshold, or None if none qualifies."""
    for release in releases:
        if release.get("draft") or release.get("prerelease"):
            continue

        tag = release["tag_name"].lstrip("v")
        published = datetime.fromisoformat(release["published_at"].replace("Z", "+00:00"))
        age = int((_now_utc() - published).total_seconds())

        if age > age_seconds:
            return tag


def fetch_releases(repo: str, per_page: int = 10) -> list[dict[str, Any]]:
    """Fetch a small sample of the most recent releases for a repository."""
    payload = subprocess.check_output(
        [
            "curl",
            "-fsSL",
            "-H",
            "Accept: application/vnd.github+json",
            "-H",
            "User-Agent: actions",
            f"https://api.github.com/repos/{repo}/releases?per_page={per_page}",
        ],
        text=True,
    )
    return json.loads(payload)


def get_eligible_release(repo: str, cutoff_seconds: int = ONE_WEEK_SECONDS) -> str | None:
    """Return the newest release older than the requested cutoff for a repository."""
    return select_release_older_than(fetch_releases(repo), cutoff_seconds)


def _write_github_output(name: str, value: str) -> None:
    """Write a key-value pair to GITHUB_OUTPUT when available."""
    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output is None:
        print(f"{name}={value}")
        return

    with Path(github_output).open("a", encoding="utf-8") as file:
        file.write(f"{name}={value}\n")


def resolve_syft_git_commit_sha(version: str) -> str:
    """Resolve the Git commit SHA for the Syft tag used by the install script.

    This is not the SHA256 of the downloaded binary. It is the Git SHA referenced by
    the install script URL in the GitHub raw content path.
    """
    result = subprocess.check_output(
        [
            "git",
            "ls-remote",
            "https://github.com/anchore/syft.git",
            f"refs/tags/v{version}^{{}}",
        ],
        text=True,
    ).strip()
    if not result:
        raise SystemExit(f"Could not resolve the Git SHA for Syft tag v{version}")
    return result.split()[0]


def update_syft_version(path: Path, version: str, git_commit_sha: str | None = None) -> None:
    """Update the pinned Syft version and the Git commit SHA used by the install script."""
    text = path.read_text(encoding="utf-8")

    updated_text, version_count = re.subn(
        r'(SYFT_VERSION:\s*")\d+\.\d+\.\d+(\")',
        rf"\g<1>{version}\2",
        text,
        count=1,
    )
    if version_count != 1:
        raise SystemExit(f"Could not find the Syft version to update in {path}")

    if git_commit_sha is None:
        git_commit_sha = resolve_syft_git_commit_sha(version)

    updated_text, sha_count = re.subn(
        r'((?:SYFT_GIT_SHA|SYFT_SHA256)\s*:\s*")[^"]*(\")',
        rf"\g<1>{git_commit_sha}\2",
        updated_text,
        count=1,
    )
    if sha_count != 1:
        raise SystemExit(f"Could not find the Syft SHA256 entry to update in {path}")

    path.write_text(updated_text, encoding="utf-8")


def update_quarto_version(path: Path, version: str) -> str:
    """Update the Quarto version and return the computed SHA256 of the downloaded .deb."""
    text = path.read_text(encoding="utf-8")
    new_text, count = re.subn(
        r'(QUARTO_VERSION:\s*")\d+\.\d+\.\d+(\")',
        rf"\g<1>{version}\2",
        text,
        count=1,
    )
    if count != 1:
        raise SystemExit(f"Could not find the Quarto version to update in {path}")

    deb_url = f"https://github.com/quarto-dev/quarto-cli/releases/download/v{version}/quarto-{version}-linux-amd64.deb"
    with tempfile.NamedTemporaryFile(suffix=".deb", delete=False) as temp_file:
        download_path = Path(temp_file.name)

    subprocess.run(["curl", "-fsSL", "-o", str(download_path), deb_url], check=True)
    new_hash = hashlib.sha256(download_path.read_bytes()).hexdigest()
    download_path.unlink(missing_ok=True)

    updated_text, hash_count = re.subn(
        r'(QUARTO_DEB_SHA256\s*:\s*")[^"]*(\")',
        rf"\g<1>{new_hash}\2",
        new_text,
        count=1,
    )
    if hash_count != 1:
        raise SystemExit(f"Could not find the Quarto SHA256 entry to update in {path}")

    path.write_text(updated_text, encoding="utf-8")
    return new_hash


def resolve_tooling_updates(
    cutoff_seconds: int = ONE_WEEK_SECONDS,
) -> tuple[str | None, str | None, str | None]:
    """Return the eligible Syft and Quarto versions, plus the Git SHA for the Syft tag."""
    syft_tag = get_eligible_release("anchore/syft", cutoff_seconds=cutoff_seconds)
    quarto_tag = get_eligible_release("quarto-dev/quarto-cli", cutoff_seconds=cutoff_seconds)
    syft_git_sha = resolve_syft_git_commit_sha(syft_tag) if syft_tag else None
    return syft_tag, syft_git_sha, quarto_tag


def apply_tooling_updates(cutoff_seconds: int = ONE_WEEK_SECONDS) -> None:
    """Resolve the eligible releases and update the action YAML files in place."""
    syft_tag, syft_git_sha, quarto_tag = resolve_tooling_updates(cutoff_seconds=cutoff_seconds)
    if syft_tag is None and quarto_tag is None:
        print("No eligible release found for Syft or Quarto. Nothing to update.")

    if syft_tag is not None:
        update_syft_version(Path("build-wheelhouse/action.yml"), syft_tag, syft_git_sha)
    if quarto_tag is not None:
        update_quarto_version(Path("_doc-build-linux/action.yml"), quarto_tag)

    print(f"Updated Syft={syft_tag or 'unchanged'}, Quarto={quarto_tag or 'unchanged'}")


def build_parser() -> argparse.ArgumentParser:
    """Create the minimal CLI parser for the workflow-only auto-update mode."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--cutoff-seconds",
        type=int,
        default=ONE_WEEK_SECONDS,
        help="Minimum age in seconds required for a release to be considered eligible.",
    )
    return parser


def main() -> None:
    """Resolve eligible releases and update the pinned tooling versions."""
    parser = build_parser()
    args = parser.parse_args()
    apply_tooling_updates(cutoff_seconds=args.cutoff_seconds)


if __name__ == "__main__":
    main()
