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
   action pushes commits, branches, and tags directly.

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
              - minor
              - major

    jobs:
      release:
        name: Auto Release
        runs-on: ubuntu-latest
        permissions:
          contents: write  # Required to push commits, branches, and tags
        steps:
          - uses: actions/checkout@v6
            with:
              fetch-depth: 0
              fetch-tags: true
              token: ${{ secrets.MY_BOT_TOKEN }}

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
