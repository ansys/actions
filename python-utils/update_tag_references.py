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
- CI/CD workflow files in .github/workflows/

Usage:
    python update_version.py <new_version>
    python update_version.py <new_version> --dry-run

Examples:
    python update_version.py 10.2.6
    python update_version.py 10.2.6 --dry-run
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

import click

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
    return version_file.read_text(encoding="utf-8").strip()


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
        click.echo(f"  [DRY RUN] Would update {version_file} to: {new_version}")
        return True

    version_file.write_text(f"{new_version}\n", encoding="utf-8")
    click.echo(f"  Updated {version_file}")
    return True


def update_pyproject(
    pyproject_path: Path,
    version_keys: list[str],
    old_version: str,
    new_version: str,
    dry_run: bool = False,
) -> bool:
    """Update version in a pyproject.toml file.

    Parameters
    ----------
    pyproject_path : Path
        Path to the pyproject.toml file.
    version_keys : list[str]
        List of keys to traverse to reach the version value.
        E.g., ["project", "version"] for [project].version
        or ["tool", "poetry", "version"] for [tool.poetry].version
    old_version : str
        Expected current version (for validation warning).
    new_version : str
        New version to set.
    dry_run : bool
        If True, only show what would be changed.

    Returns
    -------
    bool
        True if successful, False otherwise.
    """
    if not pyproject_path.exists():
        click.echo(f"  Warning: {pyproject_path} not found, skipping")
        return False

    content = pyproject_path.read_text(encoding="utf-8")
    data = tomllib.loads(content)

    # Navigate to the parent of the version key
    current_dict = data
    for key in version_keys[:-1]:
        current_dict = current_dict[key]

    version_key = version_keys[-1]
    current = current_dict[version_key]
    if current != old_version:
        click.echo(
            f"  Warning: Expected version {old_version} in {pyproject_path}, found {current}"
        )

    current_dict[version_key] = new_version

    if dry_run:
        click.echo(
            f"  [DRY RUN] Would update {pyproject_path}: version = {new_version}"
        )
        return True

    output = tomli_w.dumps(data)
    pyproject_path.write_text(output, encoding="utf-8")
    click.echo(f"  Updated {pyproject_path}")
    return True


def find_action_and_workflow_files(project_root: Path) -> list[Path]:
    """Find all action.yml files and CI/CD workflow files in the repository."""
    files = []

    # Find all action.yml files
    for action_yml in project_root.rglob("action.yml"):
        # Skip any action files in .tox, .git, or other build directories
        parts = action_yml.parts
        if ".git" in parts or ".tox" in parts:
            continue
        files.append(action_yml)

    # Find CI/CD workflow files in .github/workflows/
    workflows_dir = project_root / ".github" / "workflows"
    if workflows_dir.exists():
        for workflow_file in workflows_dir.glob("ci_cd_*.yml"):
            files.append(workflow_file)

    return sorted(files)


def update_yaml_file(
    yaml_file: Path, old_version: str, new_version: str, dry_run: bool = False
) -> int:
    """Update ansys/actions references in a YAML file.

    Returns the number of replacements made.
    """
    content = yaml_file.read_text(encoding="utf-8")

    # Pattern to match: ansys/actions/<action-name>@v<version>
    old_pattern = f"ansys/actions/([^@]+)@v{re.escape(old_version)}"
    new_replacement = f"ansys/actions/\\1@v{new_version}"

    new_content, count = re.subn(old_pattern, new_replacement, content)

    if count > 0:
        if dry_run:
            click.echo(f"  [DRY RUN] Would update {yaml_file}: {count} reference(s)")
        else:
            yaml_file.write_text(new_content, encoding="utf-8")
            click.echo(f"  Updated {yaml_file}: {count} reference(s)")

    return count


@click.command()
@click.argument("new_version")
@click.option(
    "--dry-run",
    is_flag=True,
    help="Show what would be changed without making actual changes.",
)
def main(new_version: str, dry_run: bool) -> None:
    """Update version references across the ansys/actions repository.

    NEW_VERSION is the new version to set (e.g., 10.2.6).

    \b
    Examples:
        python update_version.py 10.2.6
        python update_version.py 10.2.6 --dry-run
    """
    # Validate the new version format
    if not validate_version(new_version):
        raise click.BadParameter(
            f"Invalid version format '{new_version}'. Expected format: X.Y.Z",
            param_hint="'NEW_VERSION'",
        )

    project_root = get_project_root()
    old_version = read_current_version(project_root)

    click.echo(f"Updating version from {old_version} to {new_version}")
    if dry_run:
        click.echo("(DRY RUN - no changes will be made)\n")
    else:
        click.echo()

    if old_version == new_version:
        click.echo(
            f"Warning: New version ({new_version}) is the same as current version"
        )
        sys.exit(0)

    all_success = True
    total_refs = 0

    click.echo("1. Updating VERSION file...")
    if not update_version_file(project_root, new_version, dry_run):
        all_success = False

    click.echo("\n2. Updating .ci/ansys-actions-flit/pyproject.toml...")
    flit_path = project_root / ".ci" / "ansys-actions-flit" / "pyproject.toml"
    if not update_pyproject(
        flit_path, ["project", "version"], old_version, new_version, dry_run
    ):
        all_success = False

    click.echo("\n3. Updating .ci/ansys-actions-poetry/pyproject.toml...")
    poetry_path = project_root / ".ci" / "ansys-actions-poetry" / "pyproject.toml"
    if not update_pyproject(
        poetry_path, ["tool", "poetry", "version"], old_version, new_version, dry_run
    ):
        all_success = False

    click.echo("\n4. Updating action.yml and workflow files...")
    yaml_files = find_action_and_workflow_files(project_root)
    files_updated = 0
    for yaml_file in yaml_files:
        count = update_yaml_file(yaml_file, old_version, new_version, dry_run)
        if count > 0:
            files_updated += 1
            total_refs += count

    if total_refs == 0:
        click.echo("  No action references found to update")

    click.echo("\n" + "=" * 60)
    click.echo("Summary:")
    click.echo("  - VERSION file: updated")
    click.echo("  - pyproject.toml files: 2 updated")
    click.echo(f"  - YAML files: {files_updated} files, {total_refs} references")
    if dry_run:
        click.echo("\n(DRY RUN - no actual changes were made)")

    sys.exit(0 if all_success else 1)


if __name__ == "__main__":
    main()
