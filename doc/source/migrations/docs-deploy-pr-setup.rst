.. _docs-deploy-pr-setup:

Deploy documentation from a pull request
========================================

The ``ansys/action/doc-deploy-pr`` action handles both the deployment of html documentation from
a pull request as well as it's automatic removal once the pull request is closed. Therefore,
the ``closed`` github event must be added to ``on.pull_request.types`` to ensure that the action is
triggered for documentation removal upon pull-request closure.

The ``maximum-pr-doc-deployments`` input can be used to limit the number of documentation deployments. This is useful when multiple pull-requests exist in your repository.
more fine-grained control of which pull requests should have their documentation deployed can be
achieved via a labeling strategy.

The following comments are automatically added to the pull request depending on the exact operation
carried out by the action:

- A URL pointing to the deployed documentation.
  
- A confirmation of the removal of the documentation when the PR is closed.

- A comment when ``maximum-pr-doc-deployments`` is exceeded

Two different ways of setting up the action are proposed below, depending on the level of control desired.

1. Basic setup

   This configuration implies documentation deployment for every pull request, as long
   the limit set by ``maximum-pr-doc-deployments`` is not exceeded. This configuration is especially
   suitable for documentation-only projects where deploying the documentation for every pull request may be
   desirable (since most pull requests will involve editing the documentation). Configure your workflow
   file like below:

.. code:: yaml

    # The same action takes care of both deployment and cleanup of PR documentation
    # Add these lines to your pull request workflow file to also trigger
    # the action when the PR is closed to ensure documentation cleanup:
    on:
      pull_request:
        # opened, reopened, and synchronize are default for pull_request
        # closed - when the PR is closed (via merge or otherwise)
        types: [opened, reopened, synchronize, edited, closed]

    # Add a condition to skip other jobs in the workflow when the PR is closed
    # For example, for the doc-build job which must be run before the PR can be deployed,
    # but doesn't need to run for cleaning up the PR documentation:

    doc-build:
      name: "Doc build"
      # Skip when the PR is closed
      if: github.event.action != 'closed'
      runs-on: ubuntu-latest
      steps:
        - uses: ansys/actions/doc-build@v10
          with:
            python-version: ${{ env.MAIN_PYTHON_VERSION }}

    doc-deploy-pr:
      name: "Deploy PR documentation"
      runs-on: ubuntu-latest
      needs: doc-build
      # Run when the PR is closed i.e. when doc-build job is skipped
      if: always() && (needs.doc-build.result == 'success' || needs.doc-build.result == 'skipped')
      steps:
        - uses: ansys/actions/doc-deploy-pr@v10
          with:
            cname: ${{ env.DOCUMENTATION_CNAME }}
            token: ${{ secrets.GITHUB_TOKEN }}
            bot-user: ${{ secrets.PYANSYS_CI_BOT_USERNAME }}
            bot-email: ${{ secrets.PYANSYS_CI_BOT_EMAIL }}
            maximum-pr-doc-deployments: 10


2. Setup with a labeling strategy

   This configuration allows manually marking pull requests for documentation
   deployment using labels. This type of setup is recommended for libraries since in
   this scenario, deploying documentation for all pull requests may not be desired.

   1. Add a new label to the ``.github/labels.yml`` file.

   .. code:: yaml

       - name: 'deploy-pr-doc'
         description: Deploy pull request documentation
         color: 00ff00

   2. Add the following lines to the ``.github/labeler.yml`` file.

   .. code:: yaml

       # HACK: the label is declared with the only purpose of avoiding the
       # GitHub labeler bot from removing it. This is a known issue reported in the
       # official action/labeler repo https://github.com/actions/labeler/issues/763

       'deploy-pr-doc':
         - all:
           - changed-files:
               - all-globs-to-all-files: ['THIS-NEVER-MATCHES-A-FILE']

   3. Configure your workflow like below:

   .. code:: yaml

       # The same action takes care of both deployment and cleanup of PR documentation
       # Add these lines to your pull request workflow file to also trigger
       # the action when the PR is closed to ensure documentation cleanup:
       on:
       pull_request:
           # opened, reopened, and synchronize are default for pull_request
           # closed - when the PR is closed (via merge or otherwise)
           # labeled - for the labeling strategy to be employed
           types: [opened, reopened, synchronize, edited, labeled, closed]

       # Add a condition to skip other jobs in the workflow when the PR is closed
       # For example, for the doc-build job which must be run before the PR can be deployed,
       # but doesn't need to run for cleaning up the PR documentation:

       doc-build:
       name: "Doc build"
       # Skip when the PR is closed
       if: github.event.action != 'closed'
       runs-on: ubuntu-latest
       steps:
         - uses: ansys/actions/doc-build@v10
           with:
             python-version: ${{ env.MAIN_PYTHON_VERSION }}

       doc-deploy-pr:
       name: "Deploy PR documentation"
       runs-on: ubuntu-latest
       needs: doc-build
       # Run when the PR is closed i.e. when doc-build job is skipped
       if: |
         always() &&
         (needs.doc-build.result == 'success' || needs.doc-build.result == 'skipped') &&
         contains(github.event.pull_request.labels.*.name, 'deploy-pr-doc')
       steps:
         - uses: ansys/actions/doc-deploy-pr@v10
           with:
             cname: ${{ env.DOCUMENTATION_CNAME }}
             token: ${{ secrets.GITHUB_TOKEN }}
             bot-user: ${{ secrets.PYANSYS_CI_BOT_USERNAME }}
             bot-email: ${{ secrets.PYANSYS_CI_BOT_EMAIL }}
             maximum-pr-doc-deployments: 10

   With the instructions in the preceding steps implemented, the documentation for a pull
   request only gets deployed when ``deploy-pr-doc`` label is added to the desired
   PR. For an actual example, see `the setup <https://github.com/ansys/actions/pull/802/files>`_
   for ``ansys/actions``.