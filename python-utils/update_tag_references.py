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


class FileUpdateError(Exception):
    """Base exception for all file update operations."""

    def __init__(self, message: str, file_path: Path | None = None):
        self.message = message
        self.file_path = file_path
        super().__init__(message)


class VersionMismatchError(FileUpdateError):
    """Version in file doesn't match expected version."""

    def __init__(self, file_path: Path, expected: str, found: str):
        super().__init__(
            f"Version mismatch in {file_path}: expected {expected}, found {found}",
            file_path,
        )


PROJECT_ROOT = Path(__file__).resolve().parent.parent
VERSION_FILE_PATH = PROJECT_ROOT / "VERSION"


def is_semver(version: str) -> bool:
    """Validate that the version string matches semantic versioning pattern.

    Parameters
    ----------
    version : str
        The version string to validate.

    Returns
    -------
    bool
        True if the version matches X.Y.Z format, False otherwise.
    """
    pattern = r"^\d+\.\d+\.\d+$"
    return bool(re.match(pattern, version))


def update_version_file(
    version_file_path: Path, new_version: str, dry_run: bool = False
) -> None:
    """Update the VERSION file with the new version.

    Parameters
    ----------
    version_file_path : Path
        Path to the VERSION file.
    new_version : str
        The new version string to write.
    dry_run : bool, optional
        If True, only show what would be changed. Default is False.

    Raises
    ------
    FileUpdateError
        If the VERSION file cannot be written.
    """
    if dry_run:
        click.echo(f"  [DRY RUN] Would update {version_file_path} to: {new_version}")
        return

    try:
        version_file_path.write_text(f"{new_version}\n", encoding="utf-8")
        click.echo(f"  Updated {version_file_path}")
    except OSError as e:
        raise FileUpdateError(
            f"Failed to write VERSION file: {version_file_path}", version_file_path
        ) from e


def update_pyproject(
    pyproject_path: Path,
    version_keys: list[str],
    old_version: str,
    new_version: str,
    dry_run: bool = False,
) -> None:
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

    Raises
    ------
    FileUpdateError
        If the file cannot be read/written or has invalid TOML.
    VersionMismatchError
        If the current version doesn't match the expected version.
    """
    if not pyproject_path.exists():
        raise FileUpdateError(f"File not found: {pyproject_path}")

    try:
        content = pyproject_path.read_text(encoding="utf-8")
        data = tomllib.loads(content)
    except OSError as e:
        raise FileUpdateError(f"Failed to read {pyproject_path}", pyproject_path) from e
    except tomllib.TOMLDecodeError as e:
        raise FileUpdateError(
            f"Invalid TOML in {pyproject_path}", pyproject_path
        ) from e

    # Navigate to the parent of the version key
    try:
        current_dict = data
        for key in version_keys[:-1]:
            current_dict = current_dict[key]

        version_key = version_keys[-1]
        current = current_dict[version_key]
    except KeyError as e:
        raise FileUpdateError(
            f"Missing version key in {pyproject_path}", pyproject_path
        ) from e

    if current != old_version:
        raise VersionMismatchError(pyproject_path, old_version, current)

    current_dict[version_key] = new_version

    if dry_run:
        click.echo(
            f"  [DRY RUN] Would update {pyproject_path}: version = {new_version}"
        )
        return

    try:
        output = tomli_w.dumps(data)
        pyproject_path.write_text(output, encoding="utf-8")
        click.echo(f"  Updated {pyproject_path}")
    except OSError as e:
        raise FileUpdateError(
            f"Failed to write {pyproject_path}", pyproject_path
        ) from e


def find_action_and_workflow_files(project_root: Path) -> list[Path]:
    """Find all action.yml files and CI/CD workflow files in the repository.

    Parameters
    ----------
    project_root : Path
        Path to the project root directory.

    Returns
    -------
    list[Path]
        Sorted list of paths to action.yml and ci_cd_*.yml workflow files.
    """
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


def replace_action_refs_in_yaml_file(
    yaml_file_path: Path, old_ref: str, new_ref: str, dry_run: bool = False
) -> int:
    """Update ansys/actions references in a YAML file.

    Parameters
    ----------
    yaml_file_path : Path
        Path to the YAML file to update.
    old_ref : str
        The old version reference string to search for.
    new_ref : str
        The new version reference string to replace with.
    dry_run : bool, optional
        If True, only show what would be changed. Default is False.

    Returns
    -------
    int
        The number of replacements made.

    Raises
    ------
    FileUpdateError
        If the file cannot be read or written.
    """
    try:
        content = yaml_file_path.read_text(encoding="utf-8")
    except OSError as e:
        raise FileUpdateError(f"Failed to read {yaml_file_path}", yaml_file_path) from e

    # Pattern to match: ansys/actions/<action-name>@v<version>
    old_pattern = f"ansys/actions/([^@]+)@v{re.escape(old_ref)}"
    new_replacement = f"ansys/actions/\\1@v{new_ref}"

    new_content, count = re.subn(old_pattern, new_replacement, content)

    if count > 0:
        if dry_run:
            click.echo(
                f"  [DRY RUN] Would update {yaml_file_path}: {count} reference(s)"
            )
        else:
            try:
                yaml_file_path.write_text(new_content, encoding="utf-8")
                click.echo(f"  Updated {yaml_file_path}: {count} reference(s)")
            except OSError as e:
                raise FileUpdateError(
                    f"Failed to write {yaml_file_path}", yaml_file_path
                ) from e
    else:
        if dry_run:
            click.echo(f"  [DRY RUN] No references to update in {yaml_file_path}")
        else:
            click.echo(f"  No references to update in {yaml_file_path}")

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
    if not is_semver(new_version):
        raise click.BadParameter(
            f"Invalid version format '{new_version}'. Expected format: X.Y.Z",
            param_hint="'NEW_VERSION'",
        )

    old_version = VERSION_FILE_PATH.read_text(encoding="utf-8").strip()

    click.echo(f"Updating version from {old_version} to {new_version}")
    if dry_run:
        click.echo("(DRY RUN - no changes will be made)\n")
    else:
        click.echo()

    if old_version == new_version:
        click.echo(f"Error: New version ({new_version}) is the same as current version")
        sys.exit(1)

    errors: list[FileUpdateError] = []

    click.echo("1. Updating VERSION file...")
    try:
        update_version_file(VERSION_FILE_PATH, new_version, dry_run)
    except FileUpdateError as e:
        errors.append(e)

    click.echo("\n2. Updating .ci/ansys-actions-flit/pyproject.toml...")
    flit_path = PROJECT_ROOT / ".ci" / "ansys-actions-flit" / "pyproject.toml"
    try:
        update_pyproject(
            flit_path, ["project", "version"], old_version, new_version, dry_run
        )
    except FileUpdateError as e:
        errors.append(e)

    click.echo("\n3. Updating .ci/ansys-actions-poetry/pyproject.toml...")
    poetry_path = PROJECT_ROOT / ".ci" / "ansys-actions-poetry" / "pyproject.toml"
    try:
        update_pyproject(
            poetry_path,
            ["tool", "poetry", "version"],
            old_version,
            new_version,
            dry_run,
        )
    except FileUpdateError as e:
        errors.append(e)

    click.echo("\n4. Updating action.yml and workflow files...")
    yaml_files = find_action_and_workflow_files(PROJECT_ROOT)
    total_refs = 0
    files_updated = 0

    for yaml_file in yaml_files:
        try:
            count = replace_action_refs_in_yaml_file(
                yaml_file, old_version, new_version, dry_run
            )
            if count > 0:
                files_updated += 1
                total_refs += count
        except FileUpdateError as e:
            errors.append(e)

    if total_refs == 0:
        click.echo("  No action references found to update across all YAML files.")

    # Summary and error report
    click.echo("\n" + "=" * 60)

    if errors:
        click.secho(
            f"\nCompleted with {len(errors)} error(s):\n", fg="yellow", bold=True
        )
        for i, error in enumerate(errors, 1):
            click.secho(f"{i}. {error.message}", fg="red")
            if error.file_path:
                click.secho(f"   File: {error.file_path}", fg="red", dim=True)
        sys.exit(1)
    else:
        click.echo("Summary:")
        click.echo("  - VERSION file: updated")
        click.echo("  - pyproject.toml files: 2 updated")
        click.echo(f"  - YAML files: {files_updated} files, {total_refs} references")
        if dry_run:
            click.echo("\n(DRY RUN - no actual changes were made)")
        sys.exit(0)


if __name__ == "__main__":
    main()
