"""Sphinx documentation configuration file."""

import os
import pathlib
from datetime import datetime

import jinja2
import yaml
from ansys_sphinx_theme import ansys_favicon, get_version_match
from tabulate import tabulate as Table

# Constants used for generating documentation
DOC_SOURCE_DIR = pathlib.Path(__file__).parent.parent
DOC_DIR = DOC_SOURCE_DIR.parent
BASE_DIR = DOC_SOURCE_DIR.parent
ACTIONS_PREFIXES = ("build-", "check-", "doc-", "hk-", "release-", "tests-")
ACTIONS_SUFFIXES = "-style"
ACTIONS_INPUTS_FIELDS = ("description", "required", "type", "default")
ACCEPTED_LICENSES = BASE_DIR / "check-licenses" / "accepted-licenses.txt"
IGNORED_PACKAGES = BASE_DIR / "check-licenses" / "ignored-packages.txt"
IGNORED_SAFETY = BASE_DIR / "check-vulnerabilities" / "ignored-safety.txt"

# Project information
project = "Ansys Actions"
copyright = f"(c) 2022-{datetime.today().year} ANSYS, Inc. and/or its affiliates."
author = "ANSYS, Inc."
cname = os.getenv("DOCUMENTATION_CNAME", "actions.docs.ansys.com")

# Read version from VERSION file in base root directory
source_dir = pathlib.Path(__file__).parent.resolve().absolute()
version_file = source_dir / "../../VERSION"
with open(str(version_file), "r") as file:
    __version__ = file.read().splitlines()[0]
release = version = __version__
branch_name = (
    "main"
    if __version__.endswith("dev0")
    else f"release/{get_version_match(__version__)}"
)
actions_version = (
    "main" if __version__.endswith("dev0") else f"v{get_version_match(__version__)}"
)
switcher_version = get_version_match(__version__)

html_theme = "ansys_sphinx_theme"
html_favicon = ansys_favicon
html_short_title = html_title = project  # necessary for proper breadcrumb title
html_context = {
    "github_user": "ansys",
    "github_repo": "actions",
    "github_version": "main",
    "doc_path": "doc/source",
}


# Specify the location of your GitHub repo
html_theme_options = {
    "logo": "pyansys",
    "github_url": "https://github.com/ansys/actions",
    "use_edit_page_button": True,
    "additional_breadcrumbs": [
        ("PyAnsys", "https://docs.pyansys.com/"),
        ("PyAnsys Developer’s Guide", "https://dev.docs.pyansys.com/"),
    ],
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": switcher_version,
    },
    "cheatsheet": {
        "file": "cheat_sheet.qmd",
        "title": "Actions cheat sheet",
    },
}

# Specify Sphinx extensions to use
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx.ext.autosectionlabel",
    "sphinx_copybutton",
    "sphinx_jinja",
    "sphinx_design",
]

# Specify the static path
html_static_path = ["_static"]

# Add any paths that contain templates, relative to this directory
templates_path = ["_templates"]

# Specify the suffixes of source filenames
source_suffix = ".rst"

# Specify the master toctree document
master_doc = "index"

# Generate section labels for up to four levels
autosectionlabel_maxdepth = 2

# Ignore the following patterns when accessing links
linkcheck_ignore = [
    r"https://github.com/ansys-internal/.*",
    r"https://pkgs.dev.azure.com/pyansys/_packaging/pyansys/pypi/*",
    "https://opensource.org/blog/license/mit",  # 403 - protected from bots
]

# Auxiliary routines for automatic documentation generation


def is_valid_action_dir(path):
    """Verify if a directory is a valid action directory.

    The directory is valid if it has a valid action pattern name and contains
    an ``action.yml`` file.

    Parameters
    ----------
    path : ~pathlib.Path
        The ``Path`` instance to verify if contains an ``action.yml`` and has a valid pattern.

    Returns
    -------
    bool
        Returns ``True`` if the directory is a valid one, ``False`` otherwise.

    """
    # Verify that the path is a directory and not a file
    if not path.is_dir():
        return False

    # Verify that the path contains an action.yml file
    if not (path / "action.yml").exists():
        return False

    # Verify if is a public and registered action
    if path.name.startswith(ACTIONS_PREFIXES) or path.name.endswith(ACTIONS_SUFFIXES):
        return True

    return False


def generate_description_from_action_file(action_file):
    """Generate the description of an action from the action file.

    Parameters
    ----------
    action_file : ~pathlib.Path
        A ``Path`` object representing the action file.

    Returns
    -------
    str
        String representing description of the action.

    """
    with open(action_file, "r") as yaml_file:
        file_content = yaml.safe_load(yaml_file)
        description = file_content["description"]
        source_code_link = f"{html_theme_options['github_url']}/blob/{branch_name}/{action_file.parent.name}/action.yml"
        return (
            description
            + f"\n`Source code for this action <{source_code_link}>`__ :fab:`github`"
        )


def generate_inputs_table_from_action_file(action_file):
    """Generate the RST table containing all the input information for the action.

    Parameters
    ----------
    action_file : ~pathlib.Path
        A ``Path`` object representing the action file.

    Returns
    -------
    str
        String representing the RST table.

    """
    field_names = ("input",) + ACTIONS_INPUTS_FIELDS
    headers = [field.capitalize() for field in field_names]
    table_content = []

    with open(action_file, "r") as yaml_file:
        file_content: dict = yaml.safe_load(yaml_file)
        inputs = file_content.get("inputs", None)
        if inputs:
            for input_name, values in inputs.items():
                values = [
                    values.get(field, None) for field in field_names if field != "input"
                ]
                table_row = [input_name]
                table_row.extend(values)
                table_content.append(table_row)
        return str(Table(table_content, headers=headers, tablefmt="grid"))


# Collect all public actions directories and files
public_actions = {
    action_dir: action_dir / "action.yml"
    for action_dir in BASE_DIR.iterdir()
    if is_valid_action_dir(action_dir)
}

# Generate the Jinja contexts for the input tables
jinja_contexts = {
    action_dir.name: {
        "description": generate_description_from_action_file(action_file),
        "inputs_table": generate_inputs_table_from_action_file(action_file),
    }
    for action_dir, action_file in public_actions.items()
}


def render_example_template_with_actions_version(
    example_template_file, actions_version
):
    """Renders a example template with desired branch name.

    Parameters
    ----------
    example_template_file : ~pathlib.Path
        The ``Path`` for the example template file.
    actions_version : str
        A string representing the actions version.

    Returns
    -------
    example_rendered_file : ~pathlib.Path
        The ``Path`` for the rendered example file.

    """
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(example_template_file.parent)
    )
    example_template = env.get_template(example_template_file.name)
    content = example_template.render(version=actions_version)
    output_file_name = example_template_file.name[:-4] + "-rendered-example.yml"
    example_rendered_file = example_template_file.parent / output_file_name
    with open(example_rendered_file, "w") as file:
        file.write(content)
    return example_rendered_file


def collect_examples_from_action_name(action_name):
    """Returns a list of example files in the form of ``Path`` instances.

    Parameters
    ----------
    action_name : str
        The name of the action.

    Returns
    -------
    list[~pathlib.Path]
        A list of example files in the form of ``Path`` instances.

    """
    return [
        render_example_template_with_actions_version(path, actions_version)
        for path in DOC_SOURCE_DIR.glob("**/*")
        if path.is_file()
        and path.name.startswith(action_name)
        and not path.name.endswith("-rendered-example.yml")
    ]


def get_example_file_title(example_file):
    """Returns the title from a YML example file.

    Parameters
    ----------
    example_file : ~pathlib.Path
        The ``Path`` for the example file.

    Returns
    -------
    str
        A ``string`` representing the title of the example.

    Notes
    -----
    The string in the 'title' key of the example YML file is used. This key is
    contained within the first section of the action file, whose name is
    unknown. For this reason, the first key of the file is guessed and used
    then to retrieve the value of the 'title' key.

    """
    with open(example_file, "r") as yaml_file:
        file_content = yaml.safe_load(yaml_file)
        first_key = next(iter(file_content))
        return file_content[first_key]["name"]


# Add examples files and titles to the Jinja context for the action
for action_dir in public_actions:
    action_name = action_dir.name
    examples = collect_examples_from_action_name(action_name)
    if not len(examples):
        continue

    # Append examples to context
    jinja_contexts[action_name]["examples"] = [
        [file.name, get_example_file_title(file)] for file in examples
    ]


# Dynamically load the file contents for accepted licenses and ignored packages
def load_file_lines_as_list(file_path):
    """Loads the lines of a file in the form of a Python list.

    Parameters
    ----------
    file_path : ~pathlib.Path
        The ``Path`` instance representing the file location.

    Returns
    -------
    list[str]
        A list of strings representing the lines of the file.

    Notes
    -----
    This function is expected to be used for loading the contents of TXT files.

    """
    with open(file_path) as accepted_licenses_file:
        return list(accepted_licenses_file.read().split("\n"))


# Check licenses
for var, file in zip(
    ["accepted_licenses", "ignored_packages"], [ACCEPTED_LICENSES, IGNORED_PACKAGES]
):
    jinja_contexts["check-licenses"][var] = load_file_lines_as_list(file)

# Check vulnerabilities
jinja_contexts["check-vulnerabilities"]["ignored_safety"] = load_file_lines_as_list(
    IGNORED_SAFETY
)


def get_example_content_for_cheatsheet(example_file):
    """Get the content of an example file for the cheatsheet.

    Parameters
    ----------
    example_file : ~pathlib.Path
        The ``Path`` for the example file.

    Returns
    -------
    str
        A string representing the content of the example file.
    """
    with open(example_file, "r") as yaml_file:
        file_content = yaml.safe_load(yaml_file)
        first_key = next(iter(file_content))
        file_content = file_content[first_key]["steps"]
        return yaml.dump(file_content, default_flow_style=False)


def get_docs_link_for_action(action_file, action_name):
    """Get the link to the documentation for a specific action."""
    return f"https://{cname}/version/{switcher_version}/{action_file.parent.parent.name}/index.html#{action_name}-action"


# Generate the cheatsheet content
actions_cheatsheet_jinja_contexts = {
    action_dir.name.replace("-", " ").casefold(): {
        "examples_for_cheatsheet": [
            {
                "name": action_dir.name.replace("-", " "),
                "title": get_example_file_title(file),
                "code": get_example_content_for_cheatsheet(file),
                "reference_url": get_docs_link_for_action(file, action_dir.name),
            }
            for file in collect_examples_from_action_name(action_dir.name)
        ]
    }
    for action_dir in public_actions
}

jinja2_env = jinja2.Environment(loader=jinja2.FileSystemLoader(source_dir))
template = jinja2_env.get_template("cheat_sheet.jinja")

content = template.render(
    version=actions_version, actions=actions_cheatsheet_jinja_contexts
)
with open("cheat_sheet.qmd", "w") as cheat_sheet_file_rendered:
    cheat_sheet_file_rendered.write(content)
    cheat_sheet_file_rendered.close()
