import re
from pathlib import Path

import pypandoc
from parse_pr_title import get_towncrier_config_value, save_env_variable

"""Semantic version regex as found on semver.org:
https://semver.org/#is-there-a-suggested-regular-expression-regex-to-check-a-semver-string"""
SEMVER_REGEX = (
    r"(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
    r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
    r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
    r"(?:\+(>[0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?"
)


def get_pattern(content: str, section_title_regex: str) -> str:
    """Get the regex for locating section titles and content.

    Parameters
    ----------
    content: str
        The content of the changelog.rst or CHANGELOG.md file.
    section_title_regex: str
        The section title regex for markdown or rst.

    Returns
    -------
    str
        A string containing the regex for the section title and content in markdown or rst.
    """
    pattern = ""
    vale_regex = r"(.. vale)"
    eof_regex = r"\Z"

    # Find all strings with the following format:
    # `#.#.# <https://github.com/ansys/.../releases/tag/v#.#.#>`_ OR
    # ## [#.#.#](https://github.com/ansys/.../releases/tag/v#.#.#) - 2024-10-30
    sections = re.findall(section_title_regex, content)

    if sections:
        # If there is only one section
        if len(sections) == 1:
            if "vale on" in content:
                # Get all text from the section title to the ".. vale on" line
                pattern = rf"({section_title_regex})+([\W\w]*?)(?={vale_regex})"
            else:
                # Get all text from the section title to the end of the file
                pattern = rf"({section_title_regex})+([\W\w]*?)(?={eof_regex})"
        # If there is more than one section
        elif len(sections) > 1:
            # Get the section title and its content up to the next section title
            pattern = rf"({section_title_regex})+([\W\w]*?)(?={section_title_regex})"

    return pattern


def get_tag_section(changelog_file: Path, body: str) -> str:
    """Get the section title and content of the tag from the changelog file.

    Parameters
    ----------
    changelog_file: pathlib.Path
        The complete path to the changelog.rst or CHANGELOG.md file.
    body: str
        An empty string to be updated with the section title and content of the tag.

    Returns
    -------
    str
        A string containing the section title and content of the tag.
    """
    file_type = Path(changelog_file).name.split(".")[-1]

    with Path(changelog_file).open(encoding="utf-8") as file:
        content_lines = file.readlines()
        # Get all lines of changelog file
        content = "".join(content_lines)

        # Get the regex pattern to grab the first section in the changelog
        # containing the section title and its subsections
        if file_type.lower() == "rst":
            # For example, this pattern matches the following title:
            # `0.1.2 <https://github.com/ansys/.../releases/tag/v0.1.2>`_ - 2024-10-30
            pattern = get_pattern(content, rf"\`{SEMVER_REGEX} \<.*>\`.*")
        elif file_type.lower() == "md":
            # For example, this pattern matches the following title:
            # [0.1.2](https://github.com/ansys/.../releases/tag/v0.1.2) - 2024-10-30
            pattern = get_pattern(content, rf"## \[{SEMVER_REGEX}]\(.*\)*")

        if pattern:
            # Find the first section title and content
            match = re.search(pattern, content)

            # Access the match group containing the section title and content
            # The match.group() could look like this, for example:
            # `0.1.2 <https://github.com/ansys/.../releases/tag/v0.1.2>`_ - 2024-10-30
            # ========================================================================
            #
            # Added
            # ^^^^^
            #
            # - New feature `#1234 <https://github.com/ansys/.../pull/1234>`_
            body = match.group()

            # Convert rst to markdown
            if file_type.lower() == "rst":
                body = pypandoc.convert_text(body, "markdown_strict", format="rst")
        else:
            print("Cannot generate release notes from changelog file.")

    # Trimming first line to remove the tag and date since it is not needed for
    # the github release notes
    body = "\n".join(body.split("\n")[1:])

    return body


def get_release_notes(pyproject_path: Path):
    """Main function to create release notes from the changelog file.

    Parameters
    ----------
    pyproject_path: pathlib.Path
        The path to the pyproject.toml file.
    """
    # Set an empty string for the body of the release notes
    body = ""
    # Get the path to your changelog file: [tool.towncrier]'s filename configuration
    changelog_loc = get_towncrier_config_value("filename", pyproject_path)

    # If the changelog file exists, get the title and content for the release section
    if changelog_loc:
        body = get_tag_section(changelog_loc, body)

    # Save the env variable
    save_env_variable("RELEASE_NOTES_BODY", body)
