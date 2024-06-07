.. _docs_changelog_action_setup:

Doc-changelog action setup
==========================

The release notes for your project can either be in your documentation or the ``CHANGELOG.md`` file.
Follow the instructions in the `update the workflow <#update-the-workflow>`_ section to add the ``ansys/actions/doc-changelog`` action
to your workflow, and then choose between adding the release notes in your documentation
or the ``CHANGELOG.md`` file.

Update the workflow
-------------------

Update the ``.github/workflows/label.yml`` file to use the changelog action.

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

Next, follow the instructions to create release notes in your `documentation <#include-the-release-notes-in-your-documentation>`_ or `CHANGELOG.md file <#include-the-release-notes-in-changelog-md>`_ depending on your preference.

Include the release notes in your documentation
-----------------------------------------------

1. Create the ``doc/changelog.d`` directory and then within it add a file named ``changelog_template.jinja`` that contains the following lines:

.. code:: jinja

    {% if sections[""] %}
    {% for category, val in definitions.items() if category in sections[""] %}

    {{ definitions[category]['name'] }}
    {% set underline = '^' * definitions[category]['name']|length %}
    {{ underline }}

    {% for text, values in sections[""][category].items() %}
    - {{ text }} {{ values|join(', ') }}
    {% endfor %}

    {% endfor %}
    {% else %}
    No significant changes.


    {% endif %}

2. Create a new file named ``changelog.rst`` in the ``doc/source`` directory. Add the following lines to the file:

.. code:: rst

    .. _ref_release_notes:

    Release notes
    #############

    This document contains the release notes for the project.

    .. vale off

    .. towncrier release notes start


    .. vale on

.. note::

    If your project previously used ``CHANGELOG.md`` to record the release notes, change the description under "Release notes," replacing ``{org-name}`` and ``{repo-name}`` with the name of the organization and repository respectively, and ``{latest-version}`` with the most recent version in your ``CHANGELOG.md`` file:

    .. code:: rst

        This document contains the release notes for the project. See release notes for v{latest-version} and earlier
        in `CHANGELOG.md <https://github.com/{org-name}/{repo-name}/blob/main/CHANGELOG.md>`_.

3. Add ``changelog`` to the toctree list in the ``doc/source/index.rst`` file. ``changelog`` is placed last in the ``toctree`` list, so the "Release notes" tab is last in the documentation.

.. code:: rst

    .. toctree::
       :hidden:
       :maxdepth: 3

       <other files>
       changelog

4. Add the following lines to the ``doc/source/conf.py`` file, replacing ``{org-name}`` and ``{repo-name}`` with the name of the organization and repository respectively:

.. code:: python

    # If we are on a release, we have to ignore the "release" URLs, since it is not
    # available until the release is published.
    if switcher_version != "dev":
        linkcheck_ignore.append(
            f"https://github.com/{org-name}/{repo-name}/releases/tag/v{__version__}"
        )

.. note::

  This assumes the following code already exists in the ``doc/source/conf.py`` file:

  .. code:: python

      from ansys_sphinx_theme import get_version_match
      from ansys.<product>.<library> import __version__

      release = version = __version__
      switcher_version = get_version_match(version)

5. Add the following lines to the ``pyproject.toml`` file, replacing ``{org-name}`` and ``{repo-name}`` with the name of the organization and repository respectively.
Also, replace ``ansys.<product>.<library>`` with the name under ``tool.flit.module``. For example, ``ansys.geometry.core``.

.. code:: toml

    [tool.towncrier]
    package = "ansys.<product>.<library>"
    directory = "doc/changelog.d"
    filename = "doc/source/changelog.rst"
    start_string = ".. towncrier release notes start\n"
    template = "doc/changelog.d/changelog_template.jinja"
    title_format = "`{version} <https://github.com/{org-name}/{repo-name}/releases/tag/v{version}>`_ - {project_date}"
    issue_format = "`#{issue} <https://github.com/{org-name}/{repo-name}/pull/{issue}>`_"

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

.. note::

    If empty, the previous ``CHANGELOG.md`` file can be removed from the repository, as the changelog is now part of the documentation.

    However, if the ``CHANGELOG.md`` file is kept, it can be adapted to include the link to the documentation changelog.

    For example, the ``CHANGELOG.md`` file could look like this:

    .. code:: md

        This project uses [towncrier](https://towncrier.readthedocs.io/). Changes for the upcoming release can be found in
        [changelog.rst](doc/source/changelog.rst).

Reference pull requests for the changes can be found in the `PyAnsys Geometry <https://github.com/ansys/pyansys-geometry/pull/1138>`_ and `PyMechanical <https://github.com/ansys/pymechanical/pull/757/files>`_ repositories.
The `PyAnsys Geometry`_ pull request includes some other changes, but the changelog implementation is the same as described in this document.

Include the release notes in ``CHANGELOG.md``
---------------------------------------------

1. Create the ``doc/changelog.d`` directory and then within it add a file named ``changelog_template.jinja`` that contains the following lines:

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

2. Add the following lines to the ``CHANGELOG.md`` file, replacing ``{org-name}`` and ``{repo-name}`` with the name of the organization and repository respectively:

.. code:: md

    This project uses [towncrier](https://towncrier.readthedocs.io/) and the changes for the upcoming release can be found in <https://github.com/{org-name}/{repo-name}/tree/main/doc/changelog.d/>.

    <!-- towncrier release notes start -->


.. note::

    If the ``CHANGELOG.md`` file already has sections for previous releases, make sure to put the
    ``"towncrier release notes start"`` comment before the release sections. For example:

    .. code:: md

        <!-- towncrier release notes start -->

        ## [0.10.7](https://github.com/ansys/pymechanical/releases/tag/v0.10.7) - February 13 2024

3. Add the following lines to the ``pyproject.toml`` file, replacing ``{org-name}`` and ``{repo-name}`` with the name of the organization and repository respectively.
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

A reference pull request for these changes can be found in the `PyAnsys Geometry #1023 <https://github.com/ansys/pyansys-geometry/pull/1023/files>`_ pull request.


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

When you are ready to do a release for your repository, set up the ``ansys/actions/doc-deploy-changelog`` action
to automate the process of generating the changelog. If you want to do it manually, run the following command to
update the ``CHANGELOG.md`` file with the files in the ``changelog.d`` directory, replacing ``{version}`` with your
release number. For example, ``0.10.8``. Do not include "v" in the version:

.. code:: bash

    towncrier build --yes --version {version}

If you want to update the ``CHANGELOG.md`` file but keep the files in the ``changelog.d`` directory, run this command:

.. code:: bash

    towncrier build --keep --version {version}

If you only want to preview the changelog and not make changes to the ``CHANGELOG.md`` file,
run the following command:

.. code:: bash

    towncrier build --keep --draft --version {version}
