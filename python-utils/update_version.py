#!/usr/bin/env python

# Copyright (C) 2022 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
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
"""Update version references across the ansys/actions repository.

This script updates version references in:
- VERSION file
- .ci/ansys-actions-flit/pyproject.toml ([project].version)
- .ci/ansys-actions-poetry/pyproject.toml ([tool.poetry].version)
- All action.yml files (ansys/actions/*@vX.Y.Z references)

Usage:
    python update_version.py <new_version>
    python update_version.py <new_version> --dry-run

Examples:
    python update_version.py 10.2.6
    python update_version.py 10.2.6 --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

# tomllib is available in Python 3.11+, use tomli for older versions
try:
    import tomllib
except ImportError:
    import tomli as tomllib

import tomli_w


def get_project_root() -> Path:
    """Get the project root directory (parent of python-utils)."""
    return Path(__file__).resolve().parent.parent


def read_current_version(project_root: Path) -> str:
    """Read the current version from the VERSION file."""
    version_file = project_root / "VERSION"
    return version_file.read_text().strip()


def validate_version(version: str) -> bool:
    """Validate that the version string matches semantic versioning pattern."""
    pattern = r"^\d+\.\d+\.\d+$"
    return bool(re.match(pattern, version))


def update_version_file(
    project_root: Path, new_version: str, dry_run: bool = False
) -> bool:
    """Update the VERSION file with the new version."""
    version_file = project_root / "VERSION"
    if dry_run:
        print(f"  [DRY RUN] Would update {version_file} to: {new_version}")
        return True

    version_file.write_text(f"{new_version}\n")
    print(f"  Updated {version_file}")
    return True


def update_pyproject_flit(
    project_root: Path, old_version: str, new_version: str, dry_run: bool = False
) -> bool:
    """Update version in .ci/ansys-actions-flit/pyproject.toml."""
    pyproject_path = project_root / ".ci" / "ansys-actions-flit" / "pyproject.toml"

    if not pyproject_path.exists():
        print(f"  Warning: {pyproject_path} not found, skipping")
        return False

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    current = data.get("project", {}).get("version", "")
    if current != old_version:
        print(
            f"  Warning: Expected version {old_version} in {pyproject_path}, found {current}"
        )

    data["project"]["version"] = new_version

    if dry_run:
        print(f"  [DRY RUN] Would update {pyproject_path}: version = {new_version}")
        return True

    with open(pyproject_path, "wb") as f:
        tomli_w.dump(data, f)
    print(f"  Updated {pyproject_path}")
    return True


def update_pyproject_poetry(
    project_root: Path, old_version: str, new_version: str, dry_run: bool = False
) -> bool:
    """Update version in .ci/ansys-actions-poetry/pyproject.toml."""
    pyproject_path = project_root / ".ci" / "ansys-actions-poetry" / "pyproject.toml"

    if not pyproject_path.exists():
        print(f"  Warning: {pyproject_path} not found, skipping")
        return False

    with open(pyproject_path, "rb") as f:
        data = tomllib.load(f)

    current = data.get("tool", {}).get("poetry", {}).get("version", "")
    if current != old_version:
        print(
            f"  Warning: Expected version {old_version} in {pyproject_path}, found {current}"
        )

    data["tool"]["poetry"]["version"] = new_version

    if dry_run:
        print(f"  [DRY RUN] Would update {pyproject_path}: version = {new_version}")
        return True

    with open(pyproject_path, "wb") as f:
        tomli_w.dump(data, f)
    print(f"  Updated {pyproject_path}")
    return True


def find_action_files(project_root: Path) -> list[Path]:
    """Find all action.yml files in the repository."""
    action_files = []
    for action_yml in project_root.rglob("action.yml"):
        # Skip any action files in .tox, .git, or other build directories
        parts = action_yml.parts
        if any(part.startswith(".") and part not in (".ci",) for part in parts):
            if ".git" in parts or ".tox" in parts:
                continue
        action_files.append(action_yml)
    return sorted(action_files)


def update_action_file(
    action_file: Path, old_version: str, new_version: str, dry_run: bool = False
) -> int:
    """Update ansys/actions references in an action.yml file.

    Returns the number of replacements made.
    """
    content = action_file.read_text()

    # Pattern to match: ansys/actions/<action-name>@v<version>
    old_pattern = f"ansys/actions/([^@]+)@v{re.escape(old_version)}"
    new_replacement = f"ansys/actions/\\1@v{new_version}"

    new_content, count = re.subn(old_pattern, new_replacement, content)

    if count > 0:
        if dry_run:
            print(f"  [DRY RUN] Would update {action_file}: {count} reference(s)")
        else:
            action_file.write_text(new_content)
            print(f"  Updated {action_file}: {count} reference(s)")

    return count


def main() -> int:
    """Main entry point for the version update script."""
    parser = argparse.ArgumentParser(
        description="Update version references across the ansys/actions repository.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python update_version.py 10.2.6
    python update_version.py 10.2.6 --dry-run
        """,
    )
    parser.add_argument(
        "new_version",
        help="The new version to set (e.g., 10.2.6)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be changed without making actual changes",
    )

    args = parser.parse_args()

    # Validate the new version format
    if not validate_version(args.new_version):
        print(
            f"Error: Invalid version format '{args.new_version}'. Expected format: X.Y.Z"
        )
        return 1

    project_root = get_project_root()
    old_version = read_current_version(project_root)

    print(f"Updating version from {old_version} to {args.new_version}")
    if args.dry_run:
        print("(DRY RUN - no changes will be made)\n")
    else:
        print()

    # Check if versions are the same
    if old_version == args.new_version:
        print(
            f"Warning: New version ({args.new_version}) is the same as current version"
        )
        return 0

    # Track success
    all_success = True
    total_action_refs = 0

    # 1. Update VERSION file
    print("1. Updating VERSION file...")
    if not update_version_file(project_root, args.new_version, args.dry_run):
        all_success = False

    # 2. Update flit pyproject.toml
    print("\n2. Updating .ci/ansys-actions-flit/pyproject.toml...")
    if not update_pyproject_flit(
        project_root, old_version, args.new_version, args.dry_run
    ):
        all_success = False

    # 3. Update poetry pyproject.toml
    print("\n3. Updating .ci/ansys-actions-poetry/pyproject.toml...")
    if not update_pyproject_poetry(
        project_root, old_version, args.new_version, args.dry_run
    ):
        all_success = False

    # 4. Update all action.yml files
    print("\n4. Updating action.yml files...")
    action_files = find_action_files(project_root)
    files_updated = 0
    for action_file in action_files:
        count = update_action_file(
            action_file, old_version, args.new_version, args.dry_run
        )
        if count > 0:
            files_updated += 1
            total_action_refs += count

    if total_action_refs == 0:
        print("  No action references found to update")

    # Summary
    print("\n" + "=" * 60)
    print("Summary:")
    print("  - VERSION file: updated")
    print("  - pyproject.toml files: 2 updated")
    print(
        f"  - action.yml files: {files_updated} files, {total_action_refs} references"
    )
    if args.dry_run:
        print("\n(DRY RUN - no actual changes were made)")

    return 0 if all_success else 1


if __name__ == "__main__":
    sys.exit(main())
