Release workflow setup
======================

The ``doc-deploy-changelog`` action supports two release workflow modes:

* **Multiple-workflow-run mode** is the default. In this mode, the first workflow run updates the changelog and
  recreates the release tag using the PyAnsys CI bot. The recreated tag starts a second
  run that publishes the release.
* **Same-workflow-run mode** can be optionally enabled. In this mode, the changelog update and
  publishing jobs remain in the same workflow run initiated by the original pusher of the release tag.

Multiple-workflow-run mode is prevalent within the PyAnsys ecosystem partly because it is much easier to manage
within existing CI/CD pipelines and partly because it was the only available option for a long time.

Same-workflow-run mode was introduced to make the changelog action compatible with situations where GitHub environments
are used to enforce certain rules (such as when **Prevent self-review** is enabled to prevent the original pusher of a
tag from approving certain jobs in the workflow) whose enforcement would otherwise be circumvented by the default run mode.

Multiple-workflow-run mode
--------------------------

In the default mode, the changelog action stops the first workflow after it updates the
changelog and recreates the tag. Because the publishing jobs depend on the changelog job,
they are skipped in that run. The bot-authenticated tag push starts the workflow again.
No changelog fragments remain in the second run, so the changelog job succeeds and the
dependent publishing jobs proceed.

Use a personal access token that belongs to the PyAnsys CI bot. Unlike ``GITHUB_TOKEN``,
this credential allows the recreated tag to start the second workflow.

.. code-block:: yaml

   name: Release

   on:
     push:
       tags:
         - "v*.*.*"

   permissions: {}

   env:
     LIBRARY_NAME: ansys-example-core

   jobs:
     prepare-release:
       name: Prepare release
       runs-on: ubuntu-latest
       permissions:
         contents: write
         pull-requests: write
       steps:
         - name: Update changelog and release tag
           uses: ansys/actions/doc-deploy-changelog@v11
           with:
             token: ${{ secrets.PYANSYS_CI_BOT_TOKEN }}
             bot-user: ${{ secrets.PYANSYS_CI_BOT_USERNAME }}
             bot-email: ${{ secrets.PYANSYS_CI_BOT_EMAIL }}

     build-library:
       name: Build library
       needs: prepare-release
       runs-on: ubuntu-latest
       permissions:
         contents: read
       steps:
         - uses: ansys/actions/build-library@v11
           with:
             library-name: ${{ env.LIBRARY_NAME }}

     release:
       name: Publish release
       needs: [prepare-release, build-library]
       runs-on: ubuntu-latest
       environment: release
       permissions:
         contents: write
         id-token: write
       steps:
         - name: Download distribution artifacts
           uses: actions/download-artifact@v8
           with:
             name: ${{ env.LIBRARY_NAME }}-artifacts
             path: dist

         - name: Publish to PyPI
           uses: pypa/gh-action-pypi-publish@v1
           with:
             packages-dir: dist
             print-hash: true

         - name: Create GitHub release
           uses: ansys/actions/release-github@v11
           with:
             library-name: ${{ env.LIBRARY_NAME }}
             token: ${{ github.token }}

.. _same_workflow_release:

Same-workflow-run mode
----------------------

When ``same-workflow`` is enabled, the changelog action updates the release tag and
completes successfully. Its ``release-commit-sha`` output identifies the final commit
referenced by that tag. Jobs that test, build, or publish repository content must use
this output instead of ``github.sha``, which continues to identify the commit from the
original tag event.

Pass the repository's ``GITHUB_TOKEN`` to the changelog action. GitHub does not start a
new workflow for a tag pushed with this token, which prevents a duplicate release run.
The PYANSYS_CI_BOT token, a personal access token or GitHub App token can start another run
and should not be used for this mode.

The following workflow illustrates the relevant job structure for a typical PyAnsys
project. Adapt the example as needed for a specific project.

.. code-block:: yaml

   name: Release

   on:
     push:
       tags:
         - "v*.*.*"

   permissions: {}

   env:
     LIBRARY_NAME: ansys-example-core
     MAIN_PYTHON_VERSION: "3.12"

   jobs:
     prepare-release:
       name: Prepare release
       runs-on: ubuntu-latest
       permissions:
         contents: write
         pull-requests: write
       outputs:
         release-commit-sha: ${{ steps.changelog.outputs.release-commit-sha }}
       steps:
         - name: Update changelog and release tag
           id: changelog
           uses: ansys/actions/doc-deploy-changelog@v11
           with:
             token: ${{ github.token }}
             bot-user: github-actions[bot]
             bot-email: 41898282+github-actions[bot]@users.noreply.github.com
             same-workflow: true

     code-style:
       name: Code style
       needs: prepare-release
       runs-on: ubuntu-latest
       permissions:
         contents: read
       steps:
         - uses: actions/checkout@v6
           with:
             ref: ${{ needs.prepare-release.outputs.release-commit-sha }}
             persist-credentials: false
         - uses: ansys/actions/code-style@v11
           with:
             checkout: false

     tests:
       name: Tests
       needs: prepare-release
       runs-on: ubuntu-latest
       permissions:
         contents: read
       steps:
         - uses: actions/checkout@v6
           with:
             ref: ${{ needs.prepare-release.outputs.release-commit-sha }}
             persist-credentials: false
         - uses: ansys/actions/tests-pytest@v11
           with:
             checkout: false
             python-version: ${{ env.MAIN_PYTHON_VERSION }}

     build-library:
       name: Build library
       needs: prepare-release
       runs-on: ubuntu-latest
       permissions:
         attestations: write
         contents: read
         id-token: write
       steps:
         - uses: actions/checkout@v6
           with:
             ref: ${{ needs.prepare-release.outputs.release-commit-sha }}
             persist-credentials: false
         - uses: ansys/actions/build-library@v11
           with:
             library-name: ${{ env.LIBRARY_NAME }}
             checkout: false
             attest-provenance: true

     doc-style:
       name: Documentation style
       needs: prepare-release
       runs-on: ubuntu-latest
       permissions:
         contents: read
       steps:
         - uses: actions/checkout@v6
           with:
             ref: ${{ needs.prepare-release.outputs.release-commit-sha }}
             persist-credentials: false
         - uses: ansys/actions/doc-style@v11
           with:
             checkout: false

     doc-build:
       name: Build documentation
       needs: [prepare-release, doc-style]
       runs-on: ubuntu-latest
       permissions:
         contents: read
       steps:
         - uses: actions/checkout@v6
           with:
             ref: ${{ needs.prepare-release.outputs.release-commit-sha }}
             persist-credentials: false
         - uses: ansys/actions/doc-build@v11
           with:
             checkout: false
             python-version: ${{ env.MAIN_PYTHON_VERSION }}

     release:
       name: Publish release
       needs: [prepare-release, code-style, tests, build-library, doc-build]
       runs-on: ubuntu-latest
       environment: release
       permissions:
         contents: write
         id-token: write
       steps:
         - name: Download distribution artifacts
           uses: actions/download-artifact@v8
           with:
             name: ${{ env.LIBRARY_NAME }}-artifacts
             path: dist

         - name: Publish to PyPI
           uses: pypa/gh-action-pypi-publish@v1
           with:
             packages-dir: dist
             print-hash: true

         - name: Create GitHub release
           uses: ansys/actions/release-github@v11
           with:
             library-name: ${{ env.LIBRARY_NAME }}
             token: ${{ github.token }}
             tag-name: ${{ github.ref_name }}

The explicit checkout in each source-consuming job is required. Setting ``checkout:
false`` prevents the composite action from replacing it with the original event commit.
The ``tag-name`` passed to ``release-github`` also makes that action read changelog
content from the recreated release tag. If ``tag-name`` is omitted, the action retains
its existing behavior and uses ``github.ref_name`` for the GitHub release.
