Housekeeping actions
====================
Housekeeping actions provide for general repository operations such as package cleanup.


Package cleanup of untagged versions
------------------------------------

.. jinja:: hk-package-clean-untagged
    :file: _templates/action.rst.jinja

Package cleanup excluding certain versions
------------------------------------------

.. jinja:: hk-package-clean-except
    :file: _templates/action.rst.jinja

Auto-merge pull requests
------------------------

.. jinja:: hk-automerge-prs
    :file: _templates/action.rst.jinja

Migrate fork pull requests
---------------------------

.. jinja:: hk-migrate-fork-pr
    :file: _templates/action.rst.jinja

Tag repository version
----------------------

.. jinja:: hk-tag-repository-version
    :file: _templates/action.rst.jinja

Auto release
------------

.. important::

   This action must be used in a dedicated workflow file triggered **only**
   by ``workflow_dispatch``. Do not add other triggers (``push``,
   ``pull_request``, ``schedule``, etc.) to that workflow file, since this
   action pushes commits and tags directly to release branches (the
   main-branch dev-version bump is opened as a draft pull request instead
   of a direct push).

This action only bumps versions and manages git branches/tags for the release. It does not
build or publish anything. Use it alongside the ``release-github`` and ``release-pypi-public``
actions (typically in a separate workflow triggered by the ``vX.Y.Z`` tag this action pushes) to
actually publish the release. The main-branch version bump is opened as a **draft** pull request
specifically so it isn't merged before you've confirmed that publishing succeeded.

A plain ``patch`` release merges **all** commits from the main branch into the release branch—it
is not a cherry-pick, so every commit merged to main since the last minor/major release is
included. If you need to release only specific commits, use ``patch-cherry-pick`` with the
``cherry-pick-commits`` input instead.

If your project uses a ``uv`` or ``poetry`` lock file, set ``lock-file-tool`` to regenerate it
(via a plain ``uv lock`` or ``uvx poetry lock --no-update``) alongside each version bump, so the
lock file always reflects the just-bumped version. Neither command upgrades dependencies; they
only re-resolve the lock file against the already-bumped project metadata.

Example standalone workflow file (``.github/workflows/autorelease.yml``):

.. code-block:: yaml

    name: Auto Release

    on:
      workflow_dispatch:
        inputs:
          release_type:
            description: "Select the type of release"
            type: choice
            options:
              - patch
              - patch-cherry-pick
              - minor
              - major

    jobs:
      release:
        name: Auto Release
        runs-on: ubuntu-latest
        permissions:
          contents: write  # Required to push commits, branches, and tags
          pull-requests: write  # Required to open the dev-version-bump draft pull request
        steps:
          - name: "Auto release"
            uses: ansys/actions/hk-autorelease@v11
            with:
              release-type: ${{ github.event.inputs.release_type }}
              version-source: file
              version-location: ansys/api/geometry/VERSION
              token: ${{ secrets.MY_BOT_TOKEN }}
              bot-username: ${{ secrets.MY_BOT_USERNAME }}
              bot-email: ${{ secrets.MY_BOT_EMAIL }}

.. jinja:: hk-autorelease
    :file: _templates/action.rst.jinja
