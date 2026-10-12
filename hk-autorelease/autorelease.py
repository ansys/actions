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
