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

from pathlib import Path
import re

from packaging.version import Version
import tomlkit


class AutoReleaseError(Exception):
    """Raised for a fatal, user-facing hk-autorelease failure."""


_SETUP_PY_PATTERN = re.compile(r"(version\s*=\s*)(['\"])([^'\"]+)\2")
_MODULE_PATTERN = re.compile(r"(__version__\s*(?::\s*\w+\s*)?=\s*)(['\"])([^'\"]+)\2")


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
        match = _SETUP_PY_PATTERN.search(text)
        version = match.group(3) if match else None
    elif source == "python-module":
        match = _MODULE_PATTERN.search(text)
        version = match.group(3) if match else None
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
        pattern = _SETUP_PY_PATTERN if source == "setup-py" else _MODULE_PATTERN
        text = path.read_text(encoding="utf-8")
        new_text, count = pattern.subn(
            lambda m: f"{m.group(1)}{m.group(2)}{new_version}{m.group(2)}", text, count=1
        )
        if count == 0:
            raise AutoReleaseError(
                f"Could not find a version string in '{location}' (version-source: '{source}')."
            )
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
        raise AutoReleaseError(
            f"bump_minor_major does not support release-type '{release_type}'."
        )

    return release_version, dev_version, branch


def bump_patch(current_release_version: str) -> str:
    """Bump the patch component of ``current_release_version``."""
    version = Version(current_release_version)
    return f"{version.major}.{version.minor}.{version.micro + 1}"


_TAG_PATTERN = re.compile(r"^v(\d+)\.(\d+)\.(\d+)$")


def parse_latest_release_tag(tag_lines: list[str]) -> tuple[int, int, int]:
    """Return the ``(major, minor, patch)`` of the first ``vX.Y.Z`` tag in ``tag_lines``.

    ``tag_lines`` is expected to already be sorted from newest to oldest, as
    produced by ``git tag --list "v*" --sort=-version:refname``.
    """
    for tag in tag_lines:
        match = _TAG_PATTERN.match(tag.strip())
        if match:
            return tuple(int(part) for part in match.groups())
    raise AutoReleaseError("No 'vX.Y.Z' tags found; cannot perform a patch release.")


def classify_merge_conflict(conflicted_files: list[str], version_location: str) -> bool:
    """Return ``True`` if the only conflicting file is ``version_location``."""
    return conflicted_files == [version_location]
