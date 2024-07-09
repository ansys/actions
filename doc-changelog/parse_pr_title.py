import os


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
