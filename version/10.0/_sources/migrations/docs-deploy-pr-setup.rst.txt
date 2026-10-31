.. _docs-deploy-pr-setup:

Deploy documentation from a pull request
=========================================

The ``ansys/action/doc-deploy-pr`` action automates the deployment of HTML documentation from a pull
request (PR) and its removal when the PR is closed. To enable this, include the ``closed`` GitHub
event in ``on.pull_request.types`` to trigger documentation cleanup upon PR closure.

The ``maximum-pr-doc-deployments`` input limits the number of active documentation deployments, which
is useful for repositories with multiple PRs. You can further control deployments using a labeling
strategy.

The action automatically adds the following comments to PRs:

- A URL to the deployed documentation.
- Confirmation of documentation removal when the PR is closed.
- A notification if ``maximum-pr-doc-deployments`` is exceeded.

Two setup options are provided based on the desired level of control:

1. **Basic Setup**

   Deploy documentation for every PR, provided the ``maximum-pr-doc-deployments`` limit is not
   exceeded. This setup is ideal for documentation-focused projects. Add the following to your
   workflow file:

   .. code:: yaml

       on:
         pull_request:
           types: [opened, reopened, synchronize, edited, closed]

       jobs:
         doc-build:
           name: "Doc build"
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
           if: always() && (needs.doc-build.result == 'success' || needs.doc-build.result == 'skipped')
           steps:
             - uses: ansys/actions/doc-deploy-pr@v10
               with:
                 cname: ${{ env.DOCUMENTATION_CNAME }}
                 token: ${{ secrets.GITHUB_TOKEN }}
                 bot-user: ${{ secrets.PYANSYS_CI_BOT_USERNAME }}
                 bot-email: ${{ secrets.PYANSYS_CI_BOT_EMAIL }}
                 maximum-pr-doc-deployments: 10

2. **Setup with Labeling Strategy**

   Deploy documentation only for PRs explicitly labeled for deployment. This setup is recommended for
   libraries where deploying documentation for all PRs may not be necessary.

   Steps:

   1. Add a label to ``.github/labels.yml``:

      .. code:: yaml

          - name: 'deploy-pr-doc'
            description: Deploy pull request documentation
            color: 00ff00

   2. Add the label to ``.github/labeler.yml`` to prevent its removal:

      .. code:: yaml

          # HACK: the label is declared with the only purpose of avoiding the
          # GitHub labeler bot from removing it. This is a known issue reported in the
          # official action/labeler repo https://github.com/actions/labeler/issues/763
          'deploy-pr-doc':
            - all:
                - changed-files:
                    - all-globs-to-all-files: ['THIS-NEVER-MATCHES-A-FILE']

   3. Update your workflow file:

      .. code:: yaml

          on:
            pull_request:
              types: [opened, reopened, synchronize, edited, labeled, closed]

          jobs:
            doc-build:
              name: "Doc build"
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

   With this setup, documentation is deployed only when the ``deploy-pr-doc`` label is added to a PR.
   For an example, see `this setup <https://github.com/ansys/actions/pull/802/files>`_ for
   ``ansys/actions``.