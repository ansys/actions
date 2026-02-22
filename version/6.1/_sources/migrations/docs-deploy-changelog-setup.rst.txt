.. _docs_deploy_changelog_action_setup:

Doc-deploy-changelog action setup
=================================

When a new tag is pushed, the ``doc-deploy-changelog`` action generates a new section of the ``CHANGELOG.md`` file
if fragment files exist in their designated directory, for example ``doc/changelog.d``. By default, the
``CHANGELOG.md`` file is updated in the release branch corresponding to the tag being pushed, such as ``release/0.1``,
and a pull request is created to merge the CHANGELOG update and deleted fragment files into main.

Use the following link to set up the ``ansys/actions/doc-changelog`` action before setting up the ``doc-deploy-changelog`` action: :ref:`docs_changelog_action_setup`
Once the ``doc-changelog`` action is done being set up, continue with the ``doc-deploy-changelog`` action setup:

1. Add the ``doc-deploy-changelog`` as the first job of the ``ci_cd.yml`` file, and make the ``update-changelog`` job a requirement of the ``release`` job:

.. code:: yaml

    update-changelog:
      name: "Update CHANGELOG for new tag"
      if: github.event_name == 'push' && contains(github.ref, 'refs/tags')
      runs-on: ubuntu-latest
      permissions:
        contents: write
        pull-requests: write
      steps:
        - uses: ansys/actions/doc-deploy-changelog@{{ version }}
          with:
            token: ${{ secrets.PYANSYS_CI_BOT_TOKEN }}

    release:
      name: Release project
      if: github.event_name == 'push' && contains(github.ref, 'refs/tags')
      needs: [update-changelog]
      runs-on: ubuntu-latest
      steps:
        - name: Release to the public PyPI repository
          uses: ansys/actions/release-pypi-public@{{ version }}
          with:
            library-name: ${{ env.PACKAGE_NAME }}
            twine-username: "__token__"
            twine-token: ${{ secrets.PYPI_TOKEN }}

        - name: Release to GitHub
          uses: ansys/actions/release-github@{{ version }}
          with:
            library-name: ${{ env.PACKAGE_NAME }}

.. warning::

    `PyAnsys CI Bot <https://github.com/pyansys-ci-bot>`_ needs to be an Admin of the repository to run the `doc-deploy-changelog` action.


2. Optional - Add the ``package`` line to the ``tool.towncrier`` section of the ``pyproject.toml``. This is the same as the name under ``tool.flit.module``:

.. code:: toml

    [tool.towncrier]
    # Uses the version from the pyproject.toml instead of the tag being pushed
    package = "ansys.<product>.<library>"
