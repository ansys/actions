"""Sphinx documentation configuration file."""

import os
import pathlib

import yaml
from ansys_sphinx_theme import ansys_favicon, ansys_logo_black, get_version_match
from tabulate import tabulate as Table

# Constants used for generating documentation
DOC_SOURCE_DIR = pathlib.Path(__file__).parent.parent
DOC_DIR = DOC_SOURCE_DIR.parent
BASE_DIR = DOC_SOURCE_DIR.parent
ACTIONS_PREFIXES = ("build-", "check-", "doc-", "release-", "tests-")
ACTIONS_SUFFIXES = "-style"
ACTIONS_INPUTS_FIELDS = ("description", "required", "type", "default")

# Project information
project = "PyAnsys Actions"
copyright = "(c) 2022 ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."
cname = os.getenv("DOCUMENTATION_CNAME", "nocname.com")

# Read version from VERSION file in base root directory
source_dir = pathlib.Path(__file__).parent.resolve().absolute()
version_file = source_dir / "../../VERSION"
with open(str(version_file), "r") as file:
    __version__ = file.read().splitlines()[0]
release = version = __version__

# Use the default pyansys logo
html_logo = ansys_logo_black
html_theme = "ansys_sphinx_theme"
html_favicon = ansys_favicon

# Specify the location of your GitHub repo
html_theme_options = {
    "github_url": "https://github.com/pyansys/actions",
    "switcher": {
        "json_url": f"https://{cname}/release/versions.json",
        "version_match": get_version_match(__version__),
    },
    "navbar_end": ["version-switcher", "theme-switcher", "navbar-icon-links"],
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
autosectionlabel_maxdepth = 4


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

# Generate documentation for the action inputs in a dynamic way
jinja_contexts = {
    action_dir.name: {
        "inputs_table": generate_inputs_table_from_action_file(action_file)
    }
    for action_dir, action_file in public_actions.items()
}
