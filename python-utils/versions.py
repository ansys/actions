import os
import re
import shutil
from pathlib import Path

from packaging.version import Version


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
        raise FileNotFoundError("Could not find the versions/ directory")
    version_list = []
    excluded_versions = ["dev", "stable"]
    for version_folder in version_dir.glob("*/"):
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
            file.write(f"{var_name}={var_value}")


# def remove_files(path: Path) -> None:
#     for root, dirs, files in path.walk(top_down=False):
#         for name in files:
#             (root / name).unlink()
#         for name in dirs:
#             (root / name).rmdir()
#     path.rmdir()


def find_stable_release() -> str:
    versions_list = get_versions_list(exclude_prereleases=True)
    stable_release = max(versions_list)
    return str(stable_release)


def write_versions_file() -> None:
    TEMPLATE = """
  {{
    "name": "{name}",
    "version": "{version}",
    "url": "{url}"
  }}"""
    stable_release = find_stable_release()
    version_list = get_versions_list()
    cname = os.getenv("CNAME")
    render_last = int(os.getenv("RENDER_LAST"))
    with open("versions.json", "w", encoding="utf-8") as file:
        file.write("[")
        # version dev
        url_dev = f"https://{cname}/version/dev/"
        file.write(TEMPLATE.format(name="dev", version="dev", url=url_dev))
        file.write(",")
        # version stable
        url_stable = f"https://{cname}/version/stable/"
        file.write(
            TEMPLATE.format(
                name=f"{stable_release} (stable)",
                version=stable_release,
                url=url_stable,
            )
        )
        file.write(",")
        # Other versions
        full_list = sorted(version_list, reverse=True)
        excluding_stable = [
            version for version in full_list if version != Version(stable_release)
        ]
        counter = 1
        for version in excluding_stable:
            url_version = f"https://{cname}/version/{version}/"
            file.write(TEMPLATE.format(name=version, version=version, url=url_version))
            counter += 1
            if counter == render_last:
                file.write("\n]")
                break
            file.write(",")
        else:
            # Add 'Older versions' item
            url_older_version = f"https://{cname}/version/"
            file.write(
                TEMPLATE.format(
                    name="Older version", version="N/A", url=url_older_version
                )
            )
            file.write("\n]")
    export_to_github_output("LATEST_STABLE_VERSION", stable_release)


def set_version_variable() -> None:
    independent_patch_release = (
        True if os.getenv("INDEPENDENT_PATCH_RELEASE_DOCS") == "true" else False
    )
    tag_pattern = re.compile(
        r"""
    ^[0-9]+\.[0-9]+\.[0-9]+$ | # <MAJOR>.<MINOR>.<PATCH>
    ^[0-9]+\.[0-9]+(?:a|b|rc)[0-9]+$ # MINOR pre-release
    """,
        re.VERBOSE,
    )
    branch_pattern = re.compile(
        r"""
    ^[0-9]+\.[0-9]+$ | # <MAJOR>.<MINOR>
    ^[0-9]+\.[0-9]+\.[0-9]+ | # <MAJOR>.<MINOR>.<PATCH>
    ^[0-9]+\.[0-9]+(?:a|b|rc)[0-9]+$ # MINOR pre-release
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
            prerel
            for prerel in versions_list
            if prerel.is_prerelease
            and prerel.release == current_version.release  # MAJOR.MINOR should match
        ]
        if current_version.is_prerelease:
            # Ensure highest hierarchy of current pre-release
            valid_prerelease = all(
                current_version > prerel for prerel in existing_prereleases
            )
            if valid_prerelease:
                # Keep a maximum of 3 pre-releases
                pre_releases_to_remove = sorted(existing_prereleases, reverse=True)[3:]
                for prerel in pre_releases_to_remove:
                    prerel_path = Path(f"version/{prerel}")
                    shutil.rmtree(prerel_path)
                export_to_github_output("VERSION", str(current_version))
                export_to_github_output("PRE_RELEASE", "true")
            else:
                print("ERROR: An higher or equal pre-release version already exist")
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
                "ERROR: Tag names must follow 'vN.N.N' convention and only minor "
                "pre-releases (i.e. vN.N[{a|b|rc}N]) are supported, where 'N'"
                " is an integer."
            )
        elif ref_type == "branch":
            print(
                "ERROR: Branch names must follow 'release/N.N' or 'release/N.N.N' convention "
                "and only minor pre-release branches (i.e. release/N.N[{a|b|rc}N]) are supported,"
                " where 'N' is an integer."
            )
        exit(1)


# pattern = re.compile(
#     r"""
#     (?P<release>^[0-9]+\.[0-9]+\.[0-9]+$) | # <MAJOR>.<MINOR>.<PATCH>
#     (?P<pre>^[0-9]+\.[0-9]+(?P<pre_type>a|b|rc)(?P<pre_n>[0-9]+)$) # MINOR pre-release
#     """,
#     re.VERBOSE,
# )

# current_version = Version(version)

# existing_prereleases = [
#     prerel-
#     for prerel in versions_list
#     if prerel.is_prerelease and prerel.release == current_version.release # MAJOR.MINOR should match
# ]

# if current_version.is_prerelease:
#     pretype = current_version.pre[0]
#     match pretype:
#         case "a":
#             assert len(existing_prereleases) == 0  # There shouldn't be any prerelease
#             pass
#         case "b":
#             assert len(existing_prereleases) == 1 # Only an alpha prerelease should exist
#             pass
#         case "c":
#             assert len(existing_prereleases) == 2 # Both alpha and bete prereleases should exist
#             pass
# else: # This is a normal release
#     # All existing prereleases must be removed before the normal release
#     for prerel in existing_prereleases:
#         prerel_path = Path(f'version/{prerel}')
#         shutil.rmtree(prerel_path)

# versions_list.append(current_version)
# print(sorted(versions_list, reverse=True))
# stable_release = find_stable_release()
# write_versions_file(versions_list, stable_release)
