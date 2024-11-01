import re
from pathlib import Path

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


def rst_to_md_links(
    body: str, original_number: str, new_number: str, original_link: str, new_link: str
) -> str:
    """Convert reStructuredText, RST, links to Markdown, MD, links.

    Parameters
    ----------
    body: str
        A string containing the section title and content of the tag with RST links.
    original_number: str
        The semantic version or issue number in RST format.
        For example, "`0.1.2 " or "#123 "
    new_number: str
        The new semantic version or issue number in MD format.
        For example, "## [0.1.2]" or "[#123]"
    original_link: str
        The link in RST format. For example, "<https://github.com/ansys/.../###>`_"
    new_link: str
        The link in MD format. For example, "(https://github.com/ansys/.../###)"

    Returns
    -------
    str
        A string containing the section title and content of the tag with MD links.
    """
    # Replace "`0.1.2 " with "## [0.1.2]" or "`#123 " with "[#123]"
    body = body.replace(original_number, new_number)

    # Replace "<https://github.com/ansys/.../###>`_" with "(https://github.com/ansys/.../###)"
    body = body.replace(original_link, new_link)

    return body


def rst_to_md(body: str) -> str:
    """Convert RST text to MD.

    Parameters
    ----------
    body: str
        A string containing the changelog title and content for the most recent release in rst.

    Returns
    -------
    str
        A string containing the changelog title and content in markdown.
    """
    # Remove underline characters from the body
    underline_chars = ["=", "^"]
    for char in underline_chars:
        body = re.sub(rf"(\n|\r\n)\{char}+", "", body)

    # Add "### " to the beginning of the release subsections.
    # For example, "Added" becomes "### Added".
    body = re.sub(r"(?m)^(?=[a-zA-Z]+\s)", "### ", body)

    # Find the first string that matches the format:
    # `0.1.2 <https://github.com/ansys/.../releases/tag/v0.1.2>`_
    title_regex = re.search(rf"(`({SEMVER_REGEX})\W)(<(?<=\<)(.*?)(?=\>)>`_)", body)

    # Fix the title link
    body = rst_to_md_links(
        body,
        title_regex.group(1),
        f"## [{title_regex.group(2)}]",
        title_regex.group(8),
        f"({title_regex.group(9)})",
    )

    # Find strings that match the format: "`#1234 <https://github.com/ansys/.../pull/1234>`_"
    issue_regex = r"(`(\B#\d+)\W)(<(?<=\<)(.*?)(?=\>)>`_)"
    matches = re.findall(issue_regex, body)

    # Change all RST links, `### <...>`_, to MD links, [###](...)
    for match in matches:
        # Fix the issue links
        body = rst_to_md_links(
            body, match[0], f"[{match[1]}]", match[2], f"({match[3]})"
        )

    return body


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
                body = rst_to_md(body)
        else:
            print("Cannot generate release notes from changelog file.")

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
    print(f"CHANGELOG_LOC: {changelog_loc}")

    # If the changelog file exists, get the title and content for the release section
    if changelog_loc:
        body = get_tag_section(changelog_loc, body)

    # Save the env variable
    save_env_variable("RELEASE_NOTES_BODY", body)
