import os

import toml


def save_env_variable(env_var_name, env_var_value):
    # Get the GITHUB_ENV variable
    github_env = os.getenv("GITHUB_ENV")

    # Save environment variable with its value
    with open(github_env, "a") as f:
        f.write(f"{env_var_name}={env_var_value}")


def get_first_letter_case(pr_title):
    pr_title = f"""{pr_title}"""
    index = 0
    first_letter = pr_title[index]

    print(pr_title)

    while first_letter == " ":
        index += 1
        try:
            first_letter = pr_title[index]
        except IndexError:
            print("Pull request title is blank")
            exit(1)

    if first_letter.islower():
        save_env_variable("FIRST_LETTER", "lowercase")
    else:
        save_env_variable("FIRST_LETTER", "uppercase")


def get_conventional_commit_type(pr_title):
    pr_title = f"""{pr_title}"""
    colon_index = pr_title.index(":")
    cc_type = '"' + pr_title[:colon_index] + '"'
    save_env_variable("CC_TYPE", cc_type)


def changelog_category_cc(cc_type):
    # Get conventional commit type from env variable
    cc_type = cc_type.lower()

    print(cc_type)

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

    changelog_section = cc_type_changelog_dict[cc_type]

    save_env_variable("CHANGELOG_SECTION", changelog_section)


def changelog_cateogry_labels(labels):
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

    def get_changelog_section(pr_labels, existing_labels):
        """Find the changelog section corresponding to the label in the PR."""
        label_type = ""

        for key, value in pr_labels.items():
            if key in existing_labels:
                label_type = value
                return label_type

        # If no labels are in the PR, it goes into the miscellaneous category
        label_type = "miscellaneous"
        return label_type

    save_env_variable(
        "CHANGELOG_SECTION", get_changelog_section(pr_labels, existing_labels)
    )


def clean_pr_title(pr_title, use_labels):
    # Retrieve title
    clean_title = pr_title

    # If not using label, remove conventional commit type from title
    if use_labels == "False":
        colon_index = clean_title.index(":")
        clean_title = clean_title[colon_index + 1 :]

    print(clean_title)

    # Remove extra whitespace
    clean_title = clean_title.strip()

    # Add backslash in front of backtick and double quote
    clean_title = clean_title.replace("`", "\\`").replace('"', '\\"')

    save_env_variable("CLEAN_TITLE", clean_title)


def add_towncrier_config(org_name, repo_name, web_release_notes):
    # Load pyproject.toml file
    with open("pyproject.toml", "a+") as file:
        config = toml.load("pyproject.toml")
        tool = config.get("tool", "DNE")
        towncrier = tool.get("towncrier", "DNE")
        changelog_sections = [
            "added",
            "dependencies",
            "documentation",
            "fixed",
            "maintenance",
            "miscellaneous",
            "test",
        ]

        # Get the package name from [tool.flit.module]
        flit = tool.get("flit", "DNE")
        module = name = package = ""
        if flit != "DNE":
            module = flit.get("module", "DNE")
            if module != ("DNE" or ""):
                name = module.get("name", "DNE")

        # If [tool.flit.module] name exists, create the package string
        if name != ("DNE" and ""):
            package = f'package = "{name}"'

        # If the [tool.towncrier] section does not exist
        if towncrier == "DNE":
            # Append the tool.towncrier section
            file.write("\n[tool.towncrier]\n")

            # Write the package line if [tool.flit.module] name exists
            if package:
                file.write(f"{package}\n")

            # Write general towncrier configuration
            file.write(
                """directory = "doc/changelog.d"
underlines = ["", "", ""]
template = "doc/changelog.d/changelog_template.jinja"\n"""
            )

            # Write configuration for changelog.rst release notes
            if web_release_notes:
                file.write(
                    f"""filename = "doc/source/changelog.rst"
start_string = ".. towncrier release notes start\\n"
title_format = "`{{version}} <https://github.com/{org_name}/{repo_name}/releases/tag/v{{version}}>`_ - {{project_date}}"
issue_format = "`#{{issue}} <https://github.com/{org_name}/{repo_name}/pull/{{issue}}>`_"\n"""
                )

            # Write configuration for CHANGELOG.md release notes
            else:
                file.write(
                    f"""filename = "CHANGELOG.md"
start_string = "<!-- towncrier release notes start -->\\n"
title_format = "## [{{version}}](https://github.com/{org_name}/{repo_name}/releases/tag/v{{version}}) - {{project_date}}"
issue_format = "[#{{issue}}](https://github.com/{org_name}/{repo_name}/pull/{{issue}})"\n"""
                )
        # If [tool.towncrier] exists
        else:
            # Get the [[tool.towncrier.type]] sections
            types = towncrier.get("type", "DNE")

            # If the [[tool.towncrier.type]] sections exist
            if types != "DNE":
                for group in types:
                    # Remove changelog section if it exists under [[tool.towncrier.type]] so that
                    # only missing sections are appended to the pyproject.toml file
                    changelog_sections.remove(group["directory"])

        # Write each missing section to the pyproject.toml file
        for section in changelog_sections:
            file.write(
                f"""
[[tool.towncrier.type]]
directory = "{section}"
name = "{section.title()}"
showcontent = true\n"""
            )
