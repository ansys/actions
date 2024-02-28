.. doc-changelog action setup:

Doc-changelog action setup
==========================

To set up your repository to use ``ansys/actions/doc-changelog``, see the
`changelog implementation in PyMechanical <https://github.com/ansys/pymechanical/pull/617/files>`_
or follow these steps:


1. Add the following lines to the pyproject.toml file, replacing ``{repo-name}`` with the name of the repository. For example, ``pymechanical``.

.. code:: python

    [tool.towncrier]
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

2. Create the ``doc/changelog.d`` folders, and add a file within ``changelog.d`` named ``changelog_template.jinja`` containing the following lines:

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

    This project uses [*towncrier*](https://towncrier.readthedocs.io/) and the changes for the upcoming release can be found in <https://github.com/ansys/{repo-name}/tree/main/changelog.d/>.

    <!-- towncrier release notes start -->

.. note::

    If ``CHANGELOG.md`` already has sections for previous releases, make sure to put the
    ``"towncrier release notes start"`` comment preceding the release sections. For example:

    .. code:: md

        <!-- towncrier release notes start -->

        ## [0.10.7](https://github.com/ansys/pymechanical/releases/tag/v0.10.7) - February 13 2024

|

4. Update ``.github/workflows/label.yml`` and ``.github/workflows/ci_cd.yml`` to use the changelog action.

Change the ``pull_request`` trigger at the top of each ``.yml`` file preceding, so it lists the pull request actions that cause the workflows to run.

.. code:: yaml

    on:
    pull_request:
        # opened, reopened, and synchronize are default for pull_request
        # edited - when PR title or body is changed
        # labeled - when labels are added to PR
        types: [opened, reopened, synchronize, edited, labeled]

At the bottom of ``.github/workflows/label.yml``, add the following lines for the changelog action:

.. code:: yaml

    changelog-fragment:
        name: "Create changelog fragment"
        needs: [labeler]
        permissions:
        contents: write
        pull-requests: write
        runs-on: ubuntu-latest
        steps:
        - uses: ansys/actions/doc-changelog@feat/changelog-action
            with:
            token: ${{ secrets.GITHUB_TOKEN }}


Setup is complete.


Towncrier commands
------------------

These commands are helpful for creating changelog fragment files manually, as well as building your ``CHANGELOG.md`` file
with the fragments in ``doc/changelog.d``.

Create a changelog file manually:

.. code:: bash

    towncrier create -c "Added a feature!" 1.added.md

.. note::

    "Added a feature!" adds the content of the file named 1.added.md.
    The number one in "1.added.md" is the pull request number and "added" is a subsection
    under the released version. For example, ``CHANGELOG.md`` would look like this if
    the preceding ``.md`` file only existed in changelog.d:

    .. code:: md

        ## [version](https://github.com/ansys/{repo-name}/releases/tag/v{version})

        ### Added

        - Added a feature! [#1](https://github.com/ansys/{repo-name}/pull/1)

|

When you are ready to do a release for your repository, run the following command to
update ``CHANGELOG.md`` with the files in changelog.d, replacing ``{version}`` with your
release number. For example, 0.10.8 - do not include "v" in the version:

.. code:: bash

    towncrier build --yes --version {version}

|

If you want to update ``CHANGELOG.md``, but keep the changelog.d files, run the following command:

.. code:: bash

    towncrier build --keep --version {version}

|

If you only want to preview the changelog, but don't want to make changes to ``CHANGELOG.md``,
run the following command:

.. code:: bash

    towncrier build --keep --draft --version {version}
