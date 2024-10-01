.. _migration_guide:

Migration guide
===============

This guide provides information on new features, breaking changes, how to migrate
from one version of the actions to another, and other upstream dependencies that
have been updated.

Version ``v8``
--------------
**Breaking changes:**

- Use secrets for commit and push credentials within ``ansys/actions/doc-changelog``,
  ``ansys/actions/doc-deploy-changelog``, ``ansys/actions/doc-deploy-dev``, and
  ``ansys/actions/doc-deploy-stable``.

**Deprecated features:**

- The ``ansys/actions/doc-deploy-index`` action has been deprecated and will be removed in the next release.
  With the deprecation of ``pymeilisearch`` and the adoption of a static search index via the ``ansys-sphinx-theme``,
  the ``ansys/actions/doc-deploy-index`` action is no longer necessary.

- The ``ansys/actions/commit-style`` action has been renamed to ``ansys/actions/check-pr-title``.

- The ``ansys/actions/branch-name-style`` actions has been removed in favor of
  `GitHub rulesets <https://dev.docs.pyansys.com/how-to/repository-protection.html#branch-protection>`_.

**Migration steps:**

- Add the following required inputs to ``ansys/actions/doc-changelog``, ``ansys/actions/doc-deploy-changelog``,
  ``ansys/actions/doc-deploy-dev``, and ``ansys/actions/doc-deploy-stable``:

.. code:: yaml

    bot-user: ${{ secrets.PYANSYS_CI_BOT_USERNAME }}
    bot-email: ${{ secrets.PYANSYS_CI_BOT_EMAIL }}

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
