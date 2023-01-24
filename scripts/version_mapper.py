"""A script for updating the JSON file controlling the version switching."""

import argparse
import json
from pathlib import Path


def sort_versions_descending(versions_list):
    """Sort a list of semantic versions in descending order.

    Parameters
    ----------
    versions_list : list[str]
        A list of strings containing the semantic versions to be sorted.

    """
    versions_list.sort(key=lambda semver: [int(digit) for digit in semver.split(".")])
    return versions_list[::-1]


def update_switch_version_file(
    json_filename,
    new_version,
    cname,
    render_last,
):
    """Add new version number and associated URL to JSON file.

    Parameters
    ----------
    json_filename : str
        File name of the version switcher JSON file.
    new_version : str
        The new version to be added to the version switcher JSON file.
    cname : str
        The canonical name of the project's documentation website.
    render_last : int
        The number of stable releases to be shown in the version switcher.

    """
    with open(f"release/{json_filename}", "r") as switcher_file:
        # Load the content of the json switcher file
        current_content = json.load(switcher_file)

        # Collect all the version numbers in the JSON file
        current_raw_versions_list = [
            data["version"] for data in current_content if data["version"] != "dev"
        ]

        # Remove the "(stable)" label to retain only version numbers
        current_versions_list = []
        for version in current_raw_versions_list:
            if version.endswith(" (stable)"):
                current_versions_list.append(version[: -len(" (stable)")])
            else:
                current_versions_list.append(version)

        # Verify if new version is already registered in the JSON file
        new_version_exists = new_version in current_versions_list
        if not new_version_exists:
            current_versions_list.append(new_version)

        # Sort all current versions in descending order
        current_versions_list = sort_versions_descending(current_versions_list)

        # Select only the desired number of versions
        if len(current_versions_list) > render_last:
            new_versions_list = current_versions_list[:render_last]
        else:
            new_versions_list = current_versions_list

        # Get the latest stable version
        latest_stable_version = new_versions_list[0]

        # Force the HTTPS in front of the CNAME
        cname = f"https://{cname}" if not cname.startswith("https://") else cname

        # Generate the new content
        new_content = []

        # The first data for the new content is always the development version
        new_content.append(dict(version="dev", url=f"{cname}/dev/"))

        # Append the information for the new content
        for ith_version, version in enumerate(new_versions_list):
            version_name = f"{version} (stable)" if ith_version == 0 else version
            new_data = dict(version=version_name, url=f"{cname}/release/{version}/")
            new_content.append(new_data)

    # Override the whole content of the version switches JSON file with the new
    # generated version data
    with open(f"release/{json_filename}", "w") as switcher_file:
        # Update JSON file with the new content
        json.dump(new_content, switcher_file, indent=4)

    # Use the latest stable version for formatting the announcement
    announcement_link = (
        f"<a href='{cname}/release/{latest_stable_version}'>{latest_stable_version}</a>"
    )
    announcement_content = f"<p>You are not viewing the most recent version of this documentation. The latest stable release is {announcement_link}.</p>"

    # Include the announcement in all available release folders. Note that
    # these are still accessible even if they are not included in the dropdown.
    release_path = Path("release")
    version_folders = [
        folder
        for folder in release_path.iterdir()
        if folder.is_dir() and folder.name != latest_stable_version
    ]

    # Inspect all the directories within each outdated version folder
    for version_folder in version_folders:
        for path in version_folder.rglob(""):

            # Skip the path if it not a directory
            if not path.is_dir():
                continue

            # Ignore private directories
            requires_announcement = True
            for dirname in str(path.relative_to(release_path)).split("/"):
                if dirname.startswith("_"):
                    requires_announcement = False
                    break

            # Generate the announcement if required
            if requires_announcement:
                announcement_file = path / "announcement.html"
                with open(announcement_file, "w") as file:
                    print(f"Writing content to {announcement_file}.")
                    file.write(announcement_content)

    # Make the redirect page to point to the latest stable
    with open("index.html", "r") as redirection_file:
        content = redirection_file.read()
    new_content = content.replace("var-url", f"{cname}/release/{latest_stable_version}/")
    with open("index.html", "w") as redirection_file:
        redirection_file.write(new_content)


def parse_cli_arguments():
    """Parse all command line arguments."""
    parser = argparse.ArgumentParser(description="Version switcher JSON file updater.")
    parser.add_argument(
        "-c", "--cname", type=str, help="Canonical name of the project's documentation."
    )
    parser.add_argument(
        "-f",
        "--json_filename",
        type=str,
        default="versions.json",
        help="Name of the JSON file controlling the version switch.",
    )
    parser.add_argument(
        "-n",
        "--new_version",
        type=str,
        help="Semantic version to be added to the version switcher.",
    )
    parser.add_argument(
        "-r",
        "--render_last",
        type=int,
        default=3,
        help="Number of latest stable versions to be included in the project's documentation.",
    )
    return parser.parse_args()


def main():
    """Entry function of the script."""
    # Parse all command line arguments
    args = parse_cli_arguments()

    # Update the version swithcher JSON file with desired information
    update_switch_version_file(
        args.json_filename,
        args.new_version,
        args.cname,
        args.render_last,
    )


if __name__ == "__main__":
    main()
