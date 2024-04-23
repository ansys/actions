.. _docs_changelog_action_setup:

Doc-changelog action setup
==========================

To set up your repository to use the ``ansys/actions/doc-changelog`` action, see
`changelog implementation in PyAnsys-Geometry <https://github.com/ansys/pyansys-geometry/pull/1023/files>`_
or follow these steps:


1. Add the following lines to the ``pyproject.toml`` file, replacing ``{repo-name}`` with the name of the repository. For example, ``pyansys-geometry``.
Also, replace ``ansys.<product>.<library>`` with the name under ``tool.flit.module``. For example, ``ansys.geometry.core``.

.. code:: toml

    [tool.towncrier]
    package = "ansys.<product>.<library>"
    directory = "doc/changelog.d"
    filename = "CHANGELOG.md"
    start_string = "<!-- towncrier release notes start -->\n"
    underlines = ["", "", ""]
    template = "doc/changelog.d/changelog_template.jinja"
    title_format = "## [{version}](https://github.com/ansys/{repo-name}/releases/tag/v{version}) - {project_date}"
    issue_format = "[#{issue}](https://github.com/ansys/{repo-name}/pull/{issue})"

    [[tool.towncrier.type]]
    directory = "added"
    name = "Added"
    showcontent = true

    [[tool.towncrier.type]]
    directory = "changed"
    name = "Changed"
    showcontent = true

    [[tool.towncrier.type]]
    directory = "fixed"
    name = "Fixed"
    showcontent = true

    [[tool.towncrier.type]]
    directory = "dependencies"
    name = "Dependencies"
    showcontent = true

    [[tool.towncrier.type]]
    directory = "miscellaneous"
    name = "Miscellaneous"
    showcontent = true

|

2. Create the ``doc/changelog.d`` directory and then within it add a file named ``changelog_template.jinja`` that contains the following lines:

.. code:: jinja

    {% if sections[""] %}
    {% for category, val in definitions.items() if category in sections[""] %}

    ### {{ definitions[category]['name'] }}

    {% for text, values in sections[""][category].items() %}
    - {{ text }} {{ values|join(', ') }}
    {% endfor %}

    {% endfor %}
    {% else %}
    No significant changes.


    {% endif %}

|

3. Add the following lines to the ``CHANGELOG.md`` file, replacing ``{repo-name}`` with the name of the repository:

.. code:: md

    This project uses [towncrier](https://towncrier.readthedocs.io/) and the changes for the upcoming release can be found in <https://github.com/ansys/{repo-name}/tree/main/doc/changelog.d/>.

    <!-- towncrier release notes start -->


.. note::

    If the ``CHANGELOG.md`` file already has sections for previous releases, make sure to put the
    ``"towncrier release notes start"`` comment before the release sections. For example:

    .. code:: md

        <!-- towncrier release notes start -->

        ## [0.10.7](https://github.com/ansys/pymechanical/releases/tag/v0.10.7) - February 13 2024

|

4. Update the ``.github/workflows/label.yml`` file to use the changelog action.

Change the ``pull_request`` trigger at the top of the preceding ``.yml`` file so that it lists the pull request actions that cause the workflows to run:

.. code:: yaml

    on:
    pull_request:
        # opened, reopened, and synchronize are default for pull_request
        # edited - when PR title or body is changed
        # labeled - when labels are added to PR
        types: [opened, reopened, synchronize, edited, labeled]

At the end of the ``.github/workflows/label.yml`` file, add the following lines for the changelog action:

.. code:: yaml

    changelog-fragment:
        name: "Create changelog fragment"
        needs: [labeler]
        permissions:
          contents: write
          pull-requests: write
        runs-on: ubuntu-latest
        steps:
        - uses: ansys/actions/doc-changelog@{{ version }}
          with:
            token: ${{ secrets.PYANSYS_CI_BOT_TOKEN }}


Implementing the changelog as part of your documentation
--------------------------------------------------------

The previous steps set up the changelog for your repository. To implement the changelog in your documentation,
some modifications have to be performed. Based on the PyAnsys libraries standards, this section assumes that
the repository has a ``docs`` directory with a Sphinx documentation setup.

1. Create a new file named ``changelog.rst`` in the ``docs`` directory. Add the following lines to the file:

.. code:: rst

    .. _ref_release_notes:

    Release notes
    #############

    This document contains the release notes for the project.

    .. vale off

    .. towncrier release notes start


    .. vale on

2. Add the ``changelog.rst`` file to the ``index.rst`` file in the ``docs`` directory.

.. code:: rst

    .. toctree::
       :hidden:
       :maxdepth: 3

       changelog
       <other files>


3. Add the following lines to the ``conf.py`` file in the ``docs`` directory, replacing ``{repo-name}``
   and ``{org-name}`` with the name of the repository:

.. code:: python

    # If we are on a release, we have to ignore the "release" URLs, since it is not
    # available until the release is published.
    if switcher_version != "dev":
        linkcheck_ignore.append(
            f"https://github.com/{org-name}/{repo-name}/releases/tag/v{__version__}"
        )

4. Modify the ``pyproject.toml`` file to include the following lines, replacing ``{repo-name}``
   and ``{org-name}`` with the name of the repository:

.. code:: toml

    [tool.towncrier]
    package = "ansys.<product>.<library>"
    directory = "doc/changelog.d"
    filename = "doc/source/changelog.rst"
    start_string = ".. towncrier release notes start\n"
    template = "doc/changelog.d/changelog_template.jinja"
    title_format = "`{version} <https://github.com/{org-name}/{repo-name}/releases/tag/v{version}>`_ - {project_date}"
    issue_format = "`#{issue} <https://github.com/{org-name}/{repo-name}/pull/{issue}>`_"

.. note::

    The previous ``CHANGELOG.md`` file can be removed from the repository, as the changelog is now part of the documentation.

    However, if the ``CHANGELOG.md`` file is kept, it can be adapted to include the link to the documentation changelog.

    For example, the ``CHANGELOG.md`` file could look like this:

    .. code:: md

        This project uses [towncrier](https://towncrier.readthedocs.io/) and the
        changes for the upcoming release can be found in
        this [repository file](doc/changelog.d/changelog.rst).


A reference pull request for the changes can be found in the `PyAnsys Geometry repository <https://github.com/ansys/pyansys-geometry/pull/1138>`_.
This pull request includes some other changes, but the changelog implementation is the same as described in this document.

``towncrier`` commands
----------------------

These commands are helpful for creating changelog fragment files manually, as well as building your ``CHANGELOG.md`` file
with the fragments in the ``doc/changelog.d`` directory.

Create a changelog file manually:

.. code:: bash

    towncrier create -c "Added a feature" 1.added.md

.. note::

    "Added a feature" adds the content of the file named ``1.added.md``.
    The number one in the "1.added.md" file is the pull request number, and "added" is a subsection
    under the released version. For example, ``CHANGELOG.md`` would look like this if
    the preceding MD file only existed in the ``changelog.d`` directory:

    .. code:: md

        ## [version](https://github.com/ansys/{repo-name}/releases/tag/v{version})

        ### Added

        - Added a feature [#1](https://github.com/ansys/{repo-name}/pull/1)

|

When you are ready to do a release for your repository, run the following command to
update the ``CHANGELOG.md`` file with the files in the ``changelog.d`` directory, replacing ``{version}`` with your
release number. For example, ``0.10.8``. Do not include "v" in the version:

.. code:: bash

    towncrier build --yes --version {version}

|

If you want to update the ``CHANGELOG.md`` file but keep the files in the ``changelog.d`` directory, run this command:

.. code:: bash

    towncrier build --keep --version {version}

|

If you only want to preview the changelog and not make changes to the ``CHANGELOG.md`` file,
run the following command:

.. code:: bash

    towncrier build --keep --draft --version {version}
