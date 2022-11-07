"""Sphinx documentation configuration file."""

import pathlib

import yaml
from ansys_sphinx_theme import ansys_favicon, ansys_logo_black
from tabulate import tabulate as Table

# Project information
project = "PyAnsys Actions"
copyright = "(c) 2022 ANSYS, Inc. All rights reserved"
author = "ANSYS, Inc."

# Read version from VERSION file in base root directory
source_dir = pathlib.Path(__file__).parent.resolve().absolute()
version_file = source_dir / "../../VERSION"
with open(str(version_file), "r") as file:
    __version__ = file.read().splitlines()[0]
release = version = __version__


def get_version_match(semver):
    """Evaluate the version match for the multi-documentation."""
    if semver.endswith("dev0"):
        return "dev"
    major, minor, _ = semver.split(".")
    return ".".join([major, minor])


# Use the default pyansys logo
html_logo = ansys_logo_black
html_theme = "ansys_sphinx_theme"
html_favicon = ansys_favicon

# Specify the location of your GitHub repo
version_mapper = "https://raw.githubusercontent.com/pyansys/actions/gh-pages/release/version_mapper.json"
html_theme_options = {
    "github_url": "https://github.com/pyansys/actions",
    "show_prev_next": False,
    "switcher": {
        "json_url": version_mapper,
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


def action_file_inputs_to_rst_table(action_name):
    """Read and convert input variables of a GitHub YAML action file into a RST table.

    Parameters
    ----------
    action_file : str
        Name of the action file.

    Returns
    -------
    str
        String representing the RST table.

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
    "build-library",
    "build-ci-wheels",
    "doc-style",
    "doc-build",
    "doc-deploy-dev",
    "doc-deploy-stable",
    "release-pypi-private",
    "release-pypi-test",
    "release-pypi-public",
    "release-github",
]
jinja_contexts = {
    action_name: {"inputs_table": action_file_inputs_to_rst_table(action_name)}
    for action_name in ACTIONS_NAMES
}
