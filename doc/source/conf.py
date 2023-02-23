"""Sphinx documentation configuration file."""

import os
import pathlib
from datetime import datetime

import jinja2
import yaml
from ansys_sphinx_theme import ansys_favicon, get_version_match, pyansys_logo_black
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

# Project information
project = "PyAnsys Actions"
copyright = f"(c) 2022-{datetime.today().year} ANSYS, Inc. and/or its affiliates."
author = "ANSYS, Inc."
cname = os.getenv("DOCUMENTATION_CNAME", "nocname.com")

# Read version from VERSION file in base root directory
source_dir = pathlib.Path(__file__).parent.resolve().absolute()
version_file = source_dir / "../../VERSION"
with open(str(version_file), "r") as file:
    __version__ = file.read().splitlines()[0]
release = version = __version__
branch_name = "main" if __version__.endswith("dev0") else f"v{__version__[0]}"

# Use the default pyansys logo
html_logo = pyansys_logo_black
html_theme = "ansys_sphinx_theme"
html_favicon = ansys_favicon

# Specify the location of your GitHub repo
html_theme_options = {
    "github_url": "https://github.com/pyansys/actions",
    "switcher": {
        "json_url": f"https://{cname}/versions.json",
        "version_match": get_version_match(__version__),
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
        return file_content["description"]


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
        file_content = yaml.safe_load(yaml_file)
        inputs = file_content["inputs"]
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


def render_example_template_with_branch_name(example_template_file, branch_name):
    """Renders a example template with desired branch name.

    Parameters
    ----------
    example_template_file : ~pathlib.Path
        The ``Path`` for the example template file.
    branch_name : str
        A string representing the name of the branch.

    Returns
    -------
    example_rendered_file : ~pathlib.Path
        The ``Path`` for the rendered example file.

    """
    env = jinja2.Environment(
        loader=jinja2.FileSystemLoader(example_template_file.parent)
    )
    example_template = env.get_template(example_template_file.name)
    content = example_template.render(branch=branch_name)
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
        render_example_template_with_branch_name(path, branch_name)
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


for var, file in zip(
    ["accepted_licenses", "ignored_packages"], [ACCEPTED_LICENSES, IGNORED_PACKAGES]
):
    jinja_contexts["check-licenses"][var] = load_file_lines_as_list(file)
