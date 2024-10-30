import re
from pathlib import Path


def get_pattern(content, section_title_regex):
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

    # Get number of sections
    sections = re.findall(section_title_regex, content)

    if sections:
        # If there is only one section
        if len(sections) == 1:
            if "vale on" in content:
                pattern = rf"({section_title_regex})+([\W\w]*?){vale_regex}"
            else:
                pattern = rf"({section_title_regex})+([\W\w]*?){eof_regex}"
        # If there is more than one section
        elif len(sections) > 1:
            pattern = rf"({section_title_regex})+([\W\w]*?)({section_title_regex})"

    return pattern


def rst_to_md(body: str):
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
    # Remove the underlines
    underline_chars = ["=", "^"]
    for char in underline_chars:
        body = re.sub(rf"(\n|\r|\r\n)\{char}+", "", body)

    # Style subsection titles
    body = re.sub(r"(?m)^(?=[a-zA-Z]+\s)", "## ", body)

    # Link regex to match "`[#1234|0.1.2] <https://github.com/ansys/.../>`_"
    title_issue_regex = r"(`(\B#\d+|\d+.\d+.\d+)\W)(<(?<=\<)(.*?)(?=\>)>`_)"
    matches = re.findall(title_issue_regex, body)

    for match in matches:
        # Replace the first part of the link, either "`0.1.2 " or "#123", with "[0.1.2]" or "[#123]"
        body = body.replace(match[0], f"[{match[1]}]")
        # Replace the link, "<https://github.com/ansys/abc/releases/tag/v0.11.8>`_", with
        # "(https://github.com/ansys/abc/releases/tag/v0.11.8)"
        body = body.replace(match[2], f"({match[3]})")

    return body


def get_tag_section(changelog_file, body):
    """Get the section title and content of the tag from the changelog file.

    Parameters
    ----------
    changelog_file: pathlib.Path
        The complete path to the changelog.rst or CHANGELOG.md file.

    Returns
    -------
    str
        A string containing the section title and content of the tag.
    """
    file_type = changelog_file.name.split(".")[-1]

    with Path(changelog_file).open(encoding="utf-8") as file:
        content_lines = file.readlines()
        # Get all lines of changelog file
        content = "".join(content_lines)

        # Get the regex pattern to grab the first section in the changelog
        # containing the section title and its subsections
        if file_type.lower() == "rst":
            pattern = get_pattern(content, r"\`\d.* \<.*>\`.*")
        elif file_type.lower() == "md":
            pattern = get_pattern(content, r"## \[\d.*\(.*\)*")

        if pattern:
            # Get all section titles and content
            matches = re.findall(pattern, content)
            # Get the first section title (the most recent one)
            first_section = matches[0]
            # Combine the section title and its content into a string
            body = first_section[0] + first_section[1]

            # Convert rst to markdown
            if file_type.lower() == "rst":
                body = rst_to_md(body)
        else:
            print("Cannot generate release notes from changelog file.")

    return body
