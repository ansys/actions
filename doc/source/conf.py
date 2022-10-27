"""Sphinx documentation configuration file."""

import pathlib

import yaml
from ansys_sphinx_theme import ansys_logo_black
from tabulate import tabulate as Table

# Project information
project = "PyAnsys Actions"
copyright = "(c) 2022 ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."

# Read version from VERSION file in base root directory
source_dir = pathlib.Path(__file__).parent.resolve().absolute()
version_file = source_dir / "../../VERSION"
with open(str(version_file), "r") as file:
    __version__ = file.readlines()[0]
release = version = __version__

# use the default pyansys logo
html_logo = ansys_logo_black
html_theme = "ansys_sphinx_theme"

# specify the location of your github repo
version_mapper = "https://raw.githubusercontent.com/pyansys/actions/gh-pages/release/version_mapper.json"
html_theme_options = {
    "github_url": "https://github.com/pyansys/actions",
    "show_prev_next": False,
    "switcher": {
        "json_url": version_mapper,
        "version_match": "dev" if version.endswith("dev0") else version,
    },
    "navbar_start": ["navbar-logo", "version-switcher"],
}

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_copybutton",
    "sphinx_jinja",
]

# static path
html_static_path = ["_static"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"


def action_file_inputs_to_rst_table(action_name):
    """Read and convert input variables of a GitHub YAML action file into RST table.

    Parameters
    ----------
    action_file : ~pathlib.Path
        A path object pointing to the desired YAML file.

    Returns
    -------
    str
        A string representing the RST table.

    """
    field_names = ["input", "description", "required", "type", "default"]
    headers = [field.capitalize() for field in field_names]
    table_content = []

    with open(f"../../{action_name}/action.yml", "r") as yaml_file:
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


# Generate documentation for the action inputs in a dynamic way
ACTIONS_NAMES = [
    "code-style",
    "doc-style",
    "doc-build",
    "doc-deploy-dev",
    "doc-deploy-stable",
    "release-github",
    "release-private",
    "release-public",
]
jinja_contexts = {
    action_name: {"inputs_table": action_file_inputs_to_rst_table(action_name)}
    for action_name in ACTIONS_NAMES
}
