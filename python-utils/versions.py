import json
import os
import re
import shutil
from pathlib import Path

from packaging.version import Version

KEYS = ("name", "version", "url")


def make_entry(values: tuple[str, str, str]) -> dict:
    """Helper to create a version entry dictionary with fixed keys."""
    return dict(zip(KEYS, values))


def get_version_and_ref_type() -> tuple[str, str]:
    """Get the version and reference type from environment variables.

    Returns
    -------
    tuple[str, str]
        A tuple containing the version and reference type.
    """
    ref_type = os.getenv("REF_TYPE")
    ref_name = os.getenv("REF_NAME")
    match ref_type:
        case "tag":
            version = ref_name.split("v")[1]
        case "branch":
            version = ref_name.split("/")[1]
    return version, ref_type


def get_versions_list(exclude_prereleases: bool = False) -> list[Version]:
    """Get a list of versions from the 'version' directory.

    Parameters
    ----------
    exclude_prereleases: bool
        Prereleases are excluded from returned versions

    Returns
    -------
    list[Version]
        A list of Version objects representing the versions in the 'version' directory.
    """
    version_dir = Path("version")
    if not version_dir.exists() or not version_dir.is_dir():
        raise FileNotFoundError("Could not find the version/ directory")
    version_list = []
    excluded_versions = ["dev", "stable"]
    for version_folder in version_dir.glob("*/"):
        if version_folder.is_file():
            continue
        version_name = version_folder.name
        if version_name in excluded_versions:
            continue
        version = Version(version_name)
        if version.is_prerelease and exclude_prereleases:
            continue
        version_list.append(version)
    return version_list


def export_to_github_output(var_name: str, var_value: str) -> None:
    """Save environment variable to the GITHUB_OUTPUT file.

    Parameters
    ----------
    output_name: str
        The name of the environment variable.
    output_value: str
        The value of the environment variable.
    """
    # Get the GITHUB_OUTPUT variable
    github_output = os.getenv("GITHUB_OUTPUT")

    # Save environment variable with its value
    with open(github_output, "a") as file:
        if "\n" in var_value or "\r" in var_value:
            file.write(f"{var_name}<<EOF\n")
            file.write(var_value)
            file.write("\nEOF\n")
        else:
            file.write(f"{var_name}={var_value}\n")


def find_stable_release() -> str:
    """Find the latest stable release version.

    Returns
    -------
    str
        The latest stable release version as a string.
    """
    versions_list = get_versions_list(exclude_prereleases=True)
    stable_release = max(versions_list)
    return str(stable_release)


def write_versions_file() -> None:
    """
    Write the versions.json file with the latest stable and other versions.

    Also exports the latest stable version to the GITHUB_OUTPUT file.
    """
    cname = os.getenv("CNAME")
    render_last = int(os.getenv("RENDER_LAST"))
    stable_release = find_stable_release()
    url_stable = f"https://{cname}/version/stable/"
    content = []

    # version dev
    url_dev = f"https://{cname}/version/dev/"
    content.append(make_entry(("dev", "dev", url_dev)))

    # Other versions (including stable)
    full_list = sorted(get_versions_list(), reverse=True)
    for version in full_list[:render_last]:
        if version == Version(stable_release):
            content.append(
                make_entry((f"{stable_release} (stable)", stable_release, url_stable))
            )
            continue
        url_version = f"https://{cname}/version/{version}/"
        content.append(make_entry((str(version), str(version), url_version)))

    if len(full_list) > render_last:
        url_older_version = f"https://{cname}/version/"
        content.append(make_entry(("Older version", "N/A", url_older_version)))

    with open("versions.json", "w", encoding="utf-8") as file:
        json.dump(content, file, indent=2)

    export_to_github_output("LATEST_STABLE_VERSION", stable_release)


def set_version_variable() -> None:
    """Set the VERSION and PRE_RELEASE environment variables based on the current tag or branch.

    This function checks the current tag or branch name, validates it against a pattern,
    and sets the VERSION and PRE_RELEASE variables accordingly (i.e. exports them to GITHUB_OUTPUT
    for use in subsequent action steps). It also ensures that only the latest pre-release versions are kept.

    If the tag or branch name does not match the expected pattern, an error message is printed
    and the script exits with a non-zero status.

    If it is a normal release, it removes all existing pre-releases for that major.minor.patch version.
    """

    independent_patch_release = (
        True if os.getenv("INDEPENDENT_PATCH_RELEASE_DOCS") == "true" else False
    )
    tag_pattern = re.compile(
        r"""
    ^[0-9]+\.[0-9]+\.[0-9]+$ | # <MAJOR>.<MINOR>.<PATCH>
    ^[0-9]+\.[0-9]+\.[0-9]+(?:a|b|rc)[0-9]+$ # PATCH pre-release
    """,
        re.VERBOSE,
    )
    branch_pattern = re.compile(
        r"""
    ^[0-9]+\.[0-9]+$ | # <MAJOR>.<MINOR>
    ^[0-9]+\.[0-9]+\.[0-9]+$ | # <MAJOR>.<MINOR>.<PATCH>
    ^[0-9]+\.[0-9]+\.[0-9]+(?:a|b|rc)[0-9]+$ # PATCH pre-release
    """,
        re.VERBOSE,
    )
    version, ref_type = get_version_and_ref_type()

    if ref_type == "tag":
        match = tag_pattern.match(version)
    elif ref_type == "branch":
        match = branch_pattern.match(version)
    if match.group():
        assert version == match.group()  # Verify that version is the same as the match
        versions_list = get_versions_list()
        current_version = Version(version)
        existing_prereleases = [
            version
            for version in versions_list
            if version.is_prerelease
            and version.release
            == current_version.release  # MAJOR.MINOR.PATCH should match
        ]
        if current_version.is_prerelease:
            # Ensure highest hierarchy of current pre-release
            valid_prerelease = all(
                current_version > prerel for prerel in existing_prereleases
            )
            if valid_prerelease:
                # Keep a maximum of 3 pre-releases
                pre_releases_to_remove = sorted(existing_prereleases, reverse=True)[2:]
                for prerel in pre_releases_to_remove:
                    prerel_path = Path(f"version/{prerel}")
                    shutil.rmtree(prerel_path)
                export_to_github_output("VERSION", str(current_version))
                export_to_github_output("PRE_RELEASE", "true")
            else:
                print(
                    f"ERROR: An higher or equal pre-release version already exist: {existing_prereleases}"
                )
                exit(1)
        else:
            # All existing pre-releases must be removed before the normal release
            for prerel in existing_prereleases:
                prerel_path = Path(f"version/{prerel}")
                shutil.rmtree(prerel_path)
            if independent_patch_release:
                export_to_github_output("VERSION", str(current_version))
                export_to_github_output("PRE_RELEASE", "false")
            else:
                current_version = str(current_version).rsplit(".", 1)[
                    0
                ]  # Remove the patch number
                export_to_github_output("VERSION", str(current_version))
                export_to_github_output("PRE_RELEASE", "false")
    else:
        if ref_type == "tag":
            print(
                "ERROR: Tag names must follow 'vN.N.N' convention and only patch "
                "pre-releases (i.e. vN.N.N[{a|b|rc}N]) are supported, where 'N'"
                " is an integer."
            )
        elif ref_type == "branch":
            print(
                "ERROR: Branch names must follow 'release/N.N' or 'release/N.N.N' convention "
                "and only patch pre-release branches (i.e. release/N.N.N[{a|b|rc}N]) are supported,"
                " where 'N' is an integer."
            )
        exit(1)
