import os
from pathlib import Path

import tomli


def save_env_variable(env_var_name: str, env_var_value: str):
    """Save environment variable to the GITHUB_ENV file.

    Parameters
    ----------
    env_var_name: str
        The name of the environment variable.
    env_var_value: str
        The value of the environment variable.
    """
    # Get the GITHUB_ENV variable
    github_env = os.getenv("GITHUB_ENV")

    # Save environment variable with its value
    with open(github_env, "a") as file:
        if "\n" in env_var_value or "\r" in env_var_value:
            file.write(f"{env_var_name}<<EOF\n")
            file.write(env_var_value)
            file.write("\nEOF\n")
        else:
            file.write(f"{env_var_name}={env_var_value}")


def get_first_letter_case(pr_title: str):
    """Get the first letter of the pull request title and determine if it is uppercase or not.

    Parameters
    ----------
    pr_title: str
        The pull request title.
    """
    index = 0

    # Get the first letter of the pull request title
    first_letter = pr_title[index]

    # If the pull request title starts with a blank space, move to the next index
    # until it finds a letter
    while first_letter == " ":
        index += 1
        try:
            # Set the first letter
            first_letter = pr_title[index]
        except IndexError:
            # If the pull request title never finds a letter, the pull request title
            # is blank
            print("Pull request title is blank")
            exit(1)

    # If the first letter is lowercase, save the FIRST_LETTER environment variable
    # as lowercase. Otherwise, save it as uppercase
    if first_letter.islower():
        save_env_variable("FIRST_LETTER", "lowercase")
    else:
        save_env_variable("FIRST_LETTER", "uppercase")


def get_conventional_commit_type(pr_title: str):
    """Get the conventional commit type from the pull request title.

    Parameters
    ----------
    pr_title: str
        The pull request title.
    """
    # Get the index where the first colon is found in the pull request title
    colon_index = pr_title.index(":")
    # Get the conventional commit type from the pull request title (everything before the colon)
    cc_type = '"' + pr_title[:colon_index] + '"'
    # Save the conventional commit type as an environment variable, CC_TYPE
    save_env_variable("CC_TYPE", cc_type)


def changelog_category_cc(cc_type: str):
    """Get the changelog category based on the conventional commit type.

    Parameters
    ----------
    cc_type: str
        The conventional commit type from the pull request title.
    """
    # Get conventional commit type from the environment variable
    cc_type = cc_type.lower()

    # Dictionary whose keys are the conventional commit type and values are
    # the changelog section
    cc_type_changelog_dict = {
        "feat": "added",
        "fix": "fixed",
        "docs": "documentation",
        "build": "dependencies",
        "revert": "miscellaneous",
        "style": "miscellaneous",
        "refactor": "miscellaneous",
        "perf": "miscellaneous",
        "test": "test",
        "chore": "maintenance",
        "ci": "maintenance",
    }

    for key, value in cc_type_changelog_dict.items():
        if key in cc_type:
            # Get the changelog section based on the conventional commit type
            changelog_section = value
            break

    # Save the changelog section to the CHANGELOG_SECTION environment variable
    save_env_variable("CHANGELOG_SECTION", changelog_section)


def changelog_cateogry_labels(labels: str):
    """Get the changelog category based on the labels in the pull request.

    Parameters
    ----------
    labels: str
        String containing the labels in the pull request.
    """
    # Create a list of labels found in the pull request
    # For example, "enhancement maintenance".split() -> ["enhancement", "maintenance"]
    existing_labels = labels.split()

    # Dictionary with the key as a label from .github/workflows/label.yml and
    # value as the corresponding section in the changelog
    pr_labels = {
        "enhancement": "added",
        "bug": "fixed",
        "documentation": "documentation",
        "testing": "test",
        "dependencies": "dependencies",
        "CI/CD": "maintenance",
        "maintenance": "maintenance",
    }

    # Save the changelog section to the CHANGELOG_SECTION environment variable
    save_env_variable(
        "CHANGELOG_SECTION", get_changelog_section(pr_labels, existing_labels)
    )


def get_changelog_section(pr_labels: dict, existing_labels: list) -> str:
    """Find the changelog section corresponding to the label in the pull request.

    Parameters
    ----------
    pr_labels: dict
        Dictionary containing pull request labels and their corresponding changelog sections.
    existing_labels: list
        List of the labels that are in the pull request.

    Returns
    -------
    str
        The changelog section.
    """
    changelog_section = ""

    # For each label key and changelog section value
    for key, value in pr_labels.items():
        # If the label is in the existing_labels list
        if key in existing_labels:
            # Save the changelog section based on the label
            changelog_section = value
            return changelog_section

    # If no labels are in the PR, it goes into the miscellaneous category
    changelog_section = "miscellaneous"
    return changelog_section


def clean_pr_title(pr_title: str, use_cc: str):
    """Clean the pull request title.

    Parameters
    ----------
    pr_title: str
        The pull request title.
    use_cc: str
        Whether or not to use conventional commits to get the changelog section.
    """
    # Retrieve title
    clean_title = pr_title

    # If using conventional commits, remove it from title
    if use_cc:
        colon_index = clean_title.index(":")
        clean_title = clean_title[colon_index + 1 :]

    # Remove extra whitespace
    clean_title = clean_title.strip()

    # Add backslash in front of backtick and double quote
    clean_title = clean_title.replace("`", "\\`").replace('"', '\\"')

    # Capitalize the first word of the title
    clean_title = clean_title[0].upper() + clean_title[1:]

    # Save the clean pull request title as the CLEAN_TITLE environment variable
    save_env_variable("CLEAN_TITLE", clean_title)


def add_towncrier_config(org_name: str, repo_name: str, default_config: bool):
    """Append the missing towncrier information to the pyproject.toml file.

    Parameters
    ----------
    org_name: str
        The name of the organization.
    repo_name: str
        The name of the repository.
    default_config: bool
        Whether or not to use the default towncrier configuration for the pyproject.toml file.
    """
    pyproject_file = Path("pyproject.toml")
    towncrier_file = Path("towncrier.toml")

    if not pyproject_file.exists() and not towncrier_file.exists():
        print("No pyproject.toml or towncrier.toml file found.")
        exit(1)

    towncrier_config = pyproject_file if pyproject_file.exists() else towncrier_file
    with towncrier_config.open("rb") as file:
        config = tomli.load(file)
        tool = config.get("tool", "DNE")
        towncrier = tool.get("towncrier", "DNE")

        # List containing changelog sections under each release
        changelog_sections = [
            "added",
            "dependencies",
            "documentation",
            "fixed",
            "maintenance",
            "miscellaneous",
            "test",
        ]

        # Dictionary containing [tool.towncrier] keys and values
        towncrier_config_sections = {
            "directory": '"doc/changelog.d"',
            "template": '"doc/changelog.d/changelog_template.jinja"',
            "filename": {"web": '"doc/source/changelog.rst"', "repo": '"CHANGELOG.md"'},
            "start_string": {
                "web": '".. towncrier release notes start\\n"',
                "repo": '"<!-- towncrier release notes start -->\\n"',
            },
            "title_format": {
                "web": f'"`{{version}} <https://github.com/{org_name}/{repo_name}/releases/tag/v{{version}}>`_ - {{project_date}}"',
                "repo": f'"## [{{version}}](https://github.com/{org_name}/{repo_name}/releases/tag/v{{version}}) - {{project_date}}"',
            },
            "issue_format": {
                "web": f'"`#{{issue}} <https://github.com/{org_name}/{repo_name}/pull/{{issue}}>`_"',
                "repo": f'"[#{{issue}}](https://github.com/{org_name}/{repo_name}/pull/{{issue}})"',
            },
        }

        # Get the package name from [tool.flit.module]
        flit = tool.get("flit", "DNE")
        module = name = ""
        if flit != "DNE":
            module = flit.get("module", "DNE")
            if module != ("DNE" or ""):
                name = module.get("name", "DNE")
                # If [tool.flit.module] name exists, create the package string
                if name != ("DNE" and ""):
                    towncrier_config_sections["package"] = f'"{name}"'

        if default_config:
            # If there is no towncrier configuration information or if [[tool.towncrier.type]]
            # is the only towncrier information in the pyproject.toml file
            if towncrier == "DNE" or len(towncrier) == 1:
                # Write the [tool.towncrier] section
                write_towncrier_config_section(file, towncrier_config_sections, True)

        if towncrier != "DNE":
            # Get the existing [[tool.towncrier.type]] sections
            types = towncrier.get("type", "DNE")
            if types != "DNE":
                remove_existing_types(types, changelog_sections)

        # Add missing [[tool.towncrier.type]] sections
        write_missing_types(changelog_sections, file)


def write_towncrier_config_section(
    file, towncrier_config_sections: dict, web_release_notes: bool
):
    """Write the information in the [tool.towncrier] section.

    Parameters
    ----------
    file: _io.TextIOWrapper
        File to write to.
    towncrier_config_sections: dict
        Dictionary containing the [tool.towncrier] keys and values.
    web_release_notes: bool
        Whether or not the release notes are in the online documentation or the repository.
    """
    # Append the tool.towncrier section
    file.write("\n[tool.towncrier]\n")

    # For each key and value in the towncrier_config_sections dictionary
    for key, value in towncrier_config_sections.items():
        # If the key has values that depend on the web_release_notes boolean
        if (
            key == "filename"
            or key == "start_string"
            or key == "title_format"
            or key == "issue_format"
        ):
            # Select the value based on the web_release_notes boolean
            if web_release_notes:
                file.write(f'{key} = {value["web"]}\n')
            else:
                file.write(f'{key} = {value["repo"]}\n')
        else:
            # Write the key and value from the towncrier_config_sections dictionary
            file.write(f"{key} = {value}\n")


def remove_existing_types(types: list, changelog_sections: list):
    """Remove the existing [[tool.towncrier.types]] from the changelog_sections list.

    Parameters
    ----------
    types: list
        List of dictionaries containing information under the [[tool.towncrier.types]] sections.
    changelog_sections: list
        List containing changelog sections under each release.
    """
    for group in types:
        # Remove changelog section if it exists under [[tool.towncrier.type]] so that
        # only missing sections are appended to the pyproject.toml file
        section = group.get("directory")
        if section in changelog_sections:
            changelog_sections.remove(section)


def write_missing_types(changelog_sections: list, file):
    """Write the missing types in [[tool.towncrier.types]]

    Parameters
    ----------
    changelog_sections: list
        List containing changelog sections under each release.
    file: _io.TextIOWrapper
        File to write to.
    """
    # Write each missing section to the pyproject.toml file
    for section in changelog_sections:
        file.write(
            f"""
[[tool.towncrier.type]]
directory = "{section}"
name = "{section.title()}"
showcontent = true\n"""
        )


def get_towncrier_config_value(category: str, pyproject_path: str = "pyproject.toml"):
    """Get the value of a category within the [tool.towncrier] section of the pyproject.toml file.

    Parameters
    -----------
    category: str
        The category name within the [tool.towncrier] section you want to obtain information about.
        For example, "filename" or "directory".
    pyproject_path: str
        The path to the pyproject.toml file. By default, this is "pyproject.toml".

    Returns
    -------
    str
        The category value. If the category does not exist under [tool.towncrier], the string
        is empty.
    """
    # Get path to pyproject.toml
    pyproject_toml = Path(pyproject_path)
    # Set the category value to an empty string
    category_value = ""

    if pyproject_toml.is_file():
        # Load pyproject.toml
        with pyproject_toml.open("rb") as pyproj:
            config = tomli.load(pyproj)
            # Get the tool category in pyproject.toml
            tool = config.get("tool", "")
            if tool:
                # Get the [tool.towncrier] section in pyproject.toml
                towncrier = tool.get("towncrier", "")
                if towncrier:
                    # Get the category value under [tool.towncrier]
                    # For example, "filename" or "directory"
                    category_value = towncrier.get(category, "")

    return category_value


def rewrite_template(template_path: None, file_name: None):
    """Rewrite the template.jinja file with the default template.

    Parameters
    ----------
    template_path: str
        The path to the template.jinja file to be rewritten.
    file_name: str
        The name of the file to check if it ends with .md.

    Returns
    -------
    bool
        True if the template was rewritten, False otherwise.
    """
    template_path = template_path or "doc/changelog.d/changelog_template.jinja"
    file_name = file_name or "doc/source/changelog.rst"

    try:
        # Path to the default template file in the repository
        default_template_path = Path(__file__).parent / "default_template.jinja"

        # Path to the template.jinja file to be rewritten
        template_path = Path(template_path)

        # If filename ends with .md, do not change the template
        if file_name.endswith(".md"):
            print("The file is a markdown file. The template will not be changed.")
            return False

        # Read the content of the default template
        default_template_content = read_file_content(default_template_path)

        # Check if the content of the template.jinja file is the same as the default template
        if template_path.is_file():
            template_content = read_file_content(template_path)
            if template_content == default_template_content:
                print("The template.jinja file is already the default template.")
                return False

        # Create the necessary directories if they do not exist
        template_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the content to the template.jinja file
        write_file_content(template_path, default_template_content)
        print("The template.jinja file has been rewritten.")
        return True

    except Exception as e:
        print(f"An error occurred while rewriting the template.jinja file: {e}")
        return False


def read_file_content(file_path: Path) -> str:
    """Read the content of a file.

    Parameters
    ----------
    file_path: Path
        The path to the file to be read.

    Returns
    -------
    str
        The content of the file.
    """
    try:
        return file_path.read_text()
    except Exception as e:
        print(f"An error occurred while reading the file: {e}")


def write_file_content(file_path: Path, content: str):
    """Write content to a file, if file does not exist, create it.

    Parameters
    ----------
    file_path: Path
        The path to the file to be written.
    content: str
        The content to be written to the file.
    """
    try:
        file_path.write_text(content)
    except Exception as e:
        print(f"An error occurred while writing to the file: {e}")
