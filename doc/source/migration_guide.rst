.. _migration_guide:

Migration guide
===============

This guide provides information on new features, breaking changes, how to migrate
from one version of the actions to another, and other upstream dependencies that
have been updated.

Development version
-------------------

**New features:**

- Obscuring vulnerabilities results in ``ansys/action/check-vulnerabilities``. This is useful when you want to hide the
  vulnerabilities from the logs, but still want to fail the action if vulnerabilities are found.
- Avoid creating issues by default if vulnerabilities are found in ``ansys/action/check-vulnerabilities``.

**Breaking Changes:**

- N/A

**Migration Steps:**

- N/A

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

**Breaking Changes:**

- Multi-version documentation deployment using ``ansys/actions/doc-deploy-stable`` and ``ansys/actions/doc-deploy-dev``.

**Migration Steps:**

- Visit `Multi-version migration from ansys/actions@v3 to ansys/actions@v4 <https://dev.docs.pyansys.com/how-to/documenting.html#multi-version-migration-from-ansys-actions-v3-to-ansys-actions-v4>`_
  for a detailed migration guide.
