.. _migration_guide:

Migration guide
===============

This guide provides information on new features, breaking changes, how to migrate
from one version of the actions to another, and other upstream dependencies that
have been updated.

Version ``v10.0``
-----------------

**Breaking changes:**

- The ``ansys/actions/doc-build`` does no longer support the ``JSON`` builder
  for rendering the documentation of a project.

Version ``v9.0``
----------------

**Breaking changes:**

- Use ``ansys/actions/check-licenses`` actions with Python version 3.10 or higher.
- To use ``check-licenses: true`` with the ``ansys/actions/build-wheelhouse`` action, use Python version 3.10 or higher.
- Update your workflow to not use ``use-trusted-publisher: true`` with our pypi release actions.

  .. warning::

    Using the trusted publisher approach in ``ansys/release-pypi-public`` and ``ansys/release-pypi-private`` actions is
    not possible anymore. The reason for that is related to the action
    `pypa/gh-action-pypi-publish <https://github.com/pypa/gh-action-pypi-publish>`_ which allows to use the trusted
    publisher. Indeed, it is no longer possible to use the action in a composite action for versions after ``v1.12.0``, see
    `pypa/gh-action-pypi-publish@v1.12.0 <https://github.com/pypa/gh-action-pypi-publish/releases/tag/v1.12.0>`_.
    However, the latest versions of this action is required to upload
    `PEP 639 licensing metadata <https://packaging.python.org/en/latest/specifications/core-metadata/#license-expression>`_
    to PyPI. This allows to avoid adding upper bounds on build system like ``setuptools<=67.0.0``, ``wheel<0.46.0`` or
    ``flit_core>=3.2,<3.11``.

**Migration Steps:**

- Update input ``python-version`` to ``3.10`` or higher in the ``ansys/actions/check-licenses`` action or in
  the ``ansys/actions/build-wheelhouse`` action if you are using the ``check-licenses`` input.

  For example:

  .. code-block:: yaml

    build-wheelhouse:
      name: Build wheelhouse
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, windows-latest]
        python-version: ['3.10', '3.11', '3.12', '3.13']
    steps:
      - name: Build wheelhouse and perform smoke test
        uses: ansys/actions/build-wheelhouse@v9
        with:
          library-name: ${{ env.PACKAGE_NAME }}
          operating-system: ${{ matrix.os }}
          python-version: ${{ matrix.python-version }}

- When using trusted publisher to publish to PyPI, define you own release job instead of using the
  ``ansys/actions/release-pypi-*`` actions. See :ref:`release_pypi_trusted_publisher` for more details.

Version ``v8.2``
----------------
**New Features:**

- Added a new action named ``ansys/actions/hk-automerge-prs``. This action allows maintainers to auto-approve and merge
  ``dependabot`` PRs and ``pre-commit.ci`` PRs. It is recommended to add the action at the end of the workflow, once all the
  stages have finished successfully. That way, in case a repository has failing stages, it is not run. This action will run in case
  the PR has been created by ``dependabot`` or ``pre-commit.ci``. You can see an example of its implementation
  `here <https://github.com/ansys/pyansys/blob/e00400f3b0ad3c09d82d91a97045e6b4d3d7692c/.github/workflows/ci-build.yml#L226-L239>`_
  and the `associated PR/commit <https://github.com/ansys/pyansys/commit/e9f221428a9cc7fc64dd5f775699871288063512>`_.

- Added a new input parameter ``use-ansys-default-template`` to the ``ansys/actions/doc-changelog`` action.
  This input allows users to utilize the default template provided by the ``ansys/actions`` repository.
  For migration instructions, see the migration steps below.

  .. note::

    The default template is only available for the ``ansys/actions/doc-changelog`` action and is in the reStructuredText (rst) format.

- Added a new input parameter ``fail-level`` to the ``ansys/actions/doc-style`` action.
  This input allows users to select the report level used to control check results.
  Default value is ``"error"`` but it can be changed to ``"any"``, ``"info"``, ``"warning"``, or ``"error"``.

- The ``release-github/action.yml`` action has been improved with the ability to extend a Github release note with
  instructions on how to verify the release's artifacts attestations with
  `Github's command-line tool <https://cli.github.com/>`_.

  - Added a new input ``attest-provenance`` to the ``ansys/actions/build-library`` and ``ansys/actions/build-wheelhouse``
    actions. Note that adding provenance attestations requires write permissions for `id-token` and `attestation`.
    For example:

    .. code-block:: yaml

      build-library:
        name: Build library
        runs-on: ubuntu-latest
        permissions:
          attestations: write
          contents: read
          id-token: write
        steps:
          - name: "Build library source and wheel artifacts"
            uses: ansys/actions/build-library@v8
            with:
              library-name: ${{ env.PACKAGE_NAME }}
              python-version: ${{ env.MAIN_PYTHON_VERSION }}
              attest-provenance: true

  - Added two inputs to the ``release-github/action.yml`` action. The first input parameter
    ``add-artifact-attestation-notes`` allows users to add artifact attestation notes to the Github release notes.
    The second input parameter ``generate_release_notes`` allows users to deactivate the notes automatically generated
    by default.

- Added a new input parameter ``randomize`` to the ``ansys/actions/tests-pytest`` action to randomize the order of the tests.

**Migration Steps:**

- The default documentation includes tabs and tab items, providing a clean changelog reStructuredText (rst) file. To use this feature,
  add ``sphinx-design`` as a dependency in your ``pyproject.toml`` file and include ``sphinx_design`` as an extension in your ``conf.py`` file.

  .. code-block:: toml

    [project.optional-dependencies]
    doc = [
        "sphinx-design",
    ]

  In your ``conf.py`` file, add the following line:

  .. code-block:: python

    extensions = [
        "sphinx_design",
    ]

After updating the actions to v9, a comment is made in the PR with the changelog file, suggesting to add ``sphinx-design`` as a dependency.
You can ignore that comment if you have already added the dependency.

After merging the PR, the changelog file updates with the new template, and the new release changelog is created using the new template.

Version ``v8``
--------------
**Breaking changes:**

- Use secrets for commit and push credentials within ``ansys/actions/doc-changelog``,
  ``ansys/actions/doc-deploy-changelog``, ``ansys/actions/doc-deploy-dev``, and
  ``ansys/actions/doc-deploy-stable``.
- The token input is required in the ``ansys/actions/release-github`` action.

**Deprecated features:**

- The ``ansys/actions/doc-deploy-index`` action has been deprecated and will be
  removed in the next release. With the deprecation of ``pymeilisearch`` and
  the adoption of a static search index via the ``ansys-sphinx-theme``, the
  ``ansys/actions/doc-deploy-index`` action is no longer necessary.

- The ``ansys/actions/commit-style`` action has been renamed to
  ``ansys/actions/check-pr-title``.

- The ``ansys/actions/branch-name-style`` actions has been removed in favor of
  `GitHub rulesets
  <https://dev.docs.pyansys.com/how-to/repository-protection.html#branch-protection>`_.

**Migration steps:**

- Add the following required inputs to ``ansys/actions/doc-changelog``, ``ansys/actions/doc-deploy-changelog``,
  ``ansys/actions/doc-deploy-dev``, and ``ansys/actions/doc-deploy-stable``:

.. code:: yaml

    bot-user: ${{ secrets.PYANSYS_CI_BOT_USERNAME }}
    bot-email: ${{ secrets.PYANSYS_CI_BOT_EMAIL }}

- Add the permissions and token to the ``ansys/actions/release-github`` action as follows:

.. code:: yaml

  release-github:
    name: "Release to GitHub"
    runs-on: ubuntu-latest
    needs: [build-library]
    if: github.event_name == 'push' && contains(github.ref, 'refs/tags')
    permissions:
      contents: write
    steps:
      - name: "Release to GitHub"
        uses: ansys/actions/release-github@{{ version }}
        with:
          library-name: "ansys-<product>-<library>"
          token: ${{ secrets.GITHUB_TOKEN }}

Version ``v7``
--------------

**New features:**

- Added an optional input to the ``ansys/actions/build-library`` action to disable library build
  validation on demand using the ``validate-build: false`` argument. This is useful when you want to
  skip the library build validation step in the action.

- Incorporated the usage of `Trusted Publisher <https://docs.pypi.org/trusted-publishers/>`_ in the
  ``ansys/actions/release-pypi-*`` actions. This is useful when you want to sign the package before
  uploading it to PyPI.

**Migration steps:**

- To set up your repository to use the ``ansys/actions/release-pypi-*`` action with the `Trusted Publisher`_ approach,
  see the :ref:`release_pypi_trusted_publisher`.

Version ``v6``
--------------

**New features:**

- Added the ``ansys/actions/check-vulnerabilities`` action to check for third-party and first-party vulnerabilities.
  This is useful when you want to hide the vulnerabilities from the logs, but still want to fail the action if vulnerabilities are found.

- Avoid creating issues by default if vulnerabilities are found in the ``ansys/actions/check-vulnerabilities`` action.

- Create a changelog fragment file for each pull request using ``towncrier`` in the ``ansys/actions/doc-changelog`` action.
- Generate a new section in ``CHANGELOG.md`` if fragment files exist using ``towncrier`` in the ``ansys/actions/doc-deploy-changelog`` action.
  By default, it updates the CHANGELOG in the release branch and creates a pull request into the main branch with the updated CHANGELOG and
  deleted fragment files.

- SEO improvements. These are implemented inside the `doc-deploy-dev
  <https://actions.docs.ansys.com/version/stable/doc-actions/index.html#doc-deploy-dev-action>`_
  and the `doc-deploy-stable
  <https://actions.docs.ansys.com/version/stable/doc-actions/index.html#doc-deploy-stable-action>`_.
  Users are not required to apply any changes to their ``conf.py`` or
  ``.github/workflows/*.yml`` files. Noticable changes include:

  - No more redirect from landing page to `version/stable/index.html`
  - Generation of ``robots.txt`` file for avoiding indexing old documentation versions
  - Generation of `sitemap.xml` file for quicker indexing of `version/stable/` pages
  - Inclusion of `canonical` link tags in all HTML files for SEO purposes

- Extend ``ansys/actions/doc-build`` to be able to run in Windows runners.
  To buid the documentation in a Windows runner, we install ``Chocolatey`` and ``Miktex``.

- Allow ``ansys/actions/commit-style`` to work with upper case in the type field of a commit.
  Expected types are upper cases of  `conventional commit types
  <https://github.com/commitizen/conventional-commit-types/blob/master/index.json>`_.

**Breaking changes:**

- Upgrade default ``vale`` version from ``2.29.6`` to ``3.4.1`` in ``ansys/actions/doc-style`` action.
- Vale configuration file ``.vale.ini`` and ``Vocab/ANSYS`` has to be changed.

**Migration steps:**

- To set up your repository to use the ``ansys/actions/doc-changelog`` action, see the :ref:`docs_changelog_action_setup`.
- To set up your repository to use the ``ansys/actions/doc-deploy-changelog`` action, see the :ref:`docs_deploy_changelog_action_setup`.
- To set up your repository to use the ``ansys/actions/doc-style`` action, see the :ref:`docs_style_vale_update`.

Version ``v5``
--------------

**New features:**

- Added ``ansys/action/check-vulnerabilities`` to verify third party and first party vulnerabilities.
  This action uses ``bandit`` and ``safety`` to detect vulnerabilities in the code and dependencies, respectively.
- Added ``ansys/actions/docker-style`` to detect Dockerfile style issues using ``hadolint``.
- Allow ``vale`` version input in ``ansys/actions/doc-style`` action. By default, ``2.29.6`` is used.
- Allow using the twine ``--skip-existing`` flag in the ``ansys/actions/release-pypi-*`` actions.
- Allow using the ``ansys/actions/doc-build`` action to build documentation using a dedicated requirements file (and
  consequently, no need to have a Python project to use it).
- Allow for independent documentation releases in case of patch release when using ``ansys/actions/doc-deploy-stable`` action.
  This will create independent documentation versions for patch releases.

**Breaking changes:**

- Upgrade ``actions/upload-artifact`` and ``actions/download-artifact`` to version ``v4``.
- Upgrade ``actions/setup-python`` to version ``v5``.

**Migration steps:**

- Since artifacts are uploaded/downloaded using the new ``actions/*-artifact``, artifact names cannot
  be duplicated inside the workflow. Also, versions ``v3`` and ``v4`` are incompatible with each other. If you are using
  version ``v3`` independently inside your workflow, you need to upgrade to version ``v4``.
- The upgrade to ``actions/setup-python`` version ``v5`` is not mandatory, but it is recommended to use the latest version.
  However, it has been seen that in Windows self-hosted runners, if a certain Python version is not already stored in the
  cache, the action fails. This is a known issue and the workaround is to use the previous version of the action.

**Dependency changes:**

- Upgrade ``actions/checkout`` to version ``v4``.
- Upgrade ``pypa/cibuildwheel`` to version ``v2.16.2``.
- Upgrade ``peter-evans/create-or-update-comment`` to version ``v4``.
- Upgrade ``vimtor/action-zip`` to version ``v1.2``.


Version ``v4``
--------------

**Breaking changes:**

- Multi-version documentation deployment using ``ansys/actions/doc-deploy-stable`` and ``ansys/actions/doc-deploy-dev``.

**Migration steps:**

- Visit `Enable multi-version documentation <https://dev.docs.pyansys.com/how-to/documenting.html#enable-multi-version-documentation>`_
  for a detailed migration guide.

.. toctree::
   :hidden:
   :maxdepth: 3

   docs-changelog-setup
   docs-deploy-changelog-setup
   docs-style-vale-version-update
   release-pypi-trusted-publisher
