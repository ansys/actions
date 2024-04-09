.. _migration_guide:

Migration guide
===============

This guide provides information on new features, breaking changes, how to migrate
from one version of the actions to another, and other upstream dependencies that
have been updated.

Development version
-------------------

**New features:**

- Added the ``ansys/actions/check-vulnerabilities`` action to check for third-party and first-party vulnerabilities.
  This is useful when you want to hide the vulnerabilities from the logs, but still want to fail the action if vulnerabilities are found.
- Avoid creating issues by default if vulnerabilities are found in the ``ansys/actions/check-vulnerabilities`` action.
- Create a changelog fragment file for each pull request using ``towncrier`` in the ``ansys/actions/doc-changelog`` action.
- Vulnerability advisories can now be uploaded to the PyAnsys Dashboard using the ``ansys/actions/check-vulnerabilities`` action
  by setting the ``pyansys-dashboard-upload`` input to ``true``, together with the necessary credentials.
- Generate a new section in ``CHANGELOG.md`` if fragment files exist using ``towncrier`` in the ``ansys/actions/doc-deploy-changelog`` action.
  By default, it updates the CHANGELOG in the release branch and creates a pull request into the main branch with the updated CHANGELOG and
  deleted fragment files.

**Breaking changes:**

- N/A

**Migration steps:**

- To set up your repository to use the ``ansys/actions/doc-changelog`` action, see the :ref:`docs_changelog_action_setup`.
- To upload vulnerability advisories to the PyAnsys Dashboard, see the :ref:`pyansys_dashboard_upload`.
- To set up your repository to use the ``ansys/actions/doc-deploy-changelog`` action, see the :ref:`doc_deploy_changelog_action_setup`.

Version ``v5``
--------------

**New features:**

- Added ``ansys/action/check-vulnerabilities`` to check for third party and first party vulnerabilities.
  This action uses ``bandit`` and ``safety`` to check for vulnerabilities in the code and dependencies, respectively.
- Added ``ansys/actions/docker-style`` to check for Dockerfile style issues using ``hadolint``.
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

- Visit `Multi-version migration from ansys/actions@v3 to ansys/actions@v4 <https://dev.docs.pyansys.com/how-to/documenting.html#multi-version-migration-from-ansys-actions-v3-to-ansys-actions-v4>`_
  for a detailed migration guide.

.. toctree::
   :hidden:
   :maxdepth: 3

   docs-changelog-setup
   pyansys-dashboard-upload
