"""Sphinx documentation configuration file."""

import pathlib

from ansys_sphinx_theme import ansys_logo_black

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
html_theme_options = {
    "github_url": "https://github.com/pyansys/pyansys-template",
    "show_prev_next": False,
    "switcher": {
        "json_url": "https://raw.githubusercontent.com/pyansys/actions/gh-pages/release/version_mapper.json",
        "version_match": "dev" if version.endswith("dev0") else version,
    },
    "navbar_start": ["navbar-logo", "version-switcher"],
}

# Sphinx extensions
extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "sphinx_copybutton",
]

# static path
html_static_path = ["_static"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ["_templates"]

# The suffix(es) of source filenames.
source_suffix = ".rst"

# The master toctree document.
master_doc = "index"
