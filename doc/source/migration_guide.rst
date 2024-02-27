.. _migration_guide:

Migration guide
===============

This guide provides information on new features, breaking changes, how to migrate
from one version of the actions to another, and other upstream dependencies that
have been updated.

Development version
-------------------

**New features:**

- Obscuring vulnerabilities results in ``ansys/actions/check-vulnerabilities``. This is useful when you want to hide the
  vulnerabilities from the logs, but still want to fail the action if vulnerabilities are found.
- Avoid creating issues by default if vulnerabilities are found in ``ansys/actions/check-vulnerabilities``.
- Create a changelog fragment file for each pull request using ``towncrier`` in ``ansys/actions/doc-changelog``.

**Breaking Changes:**

- N/A

**Migration Steps:**

- To set up your repository to use ``ansys/actions/doc-changelog``, see the
  `changelog implementation in PyMechanical <https://github.com/ansys/pymechanical/pull/617>`_
  or follow these steps:

  1. Add the following lines to the pyproject.toml file,
     replacing {repo-name} with the name of the repository. For example, ``pymechanical``.

    .. code:: python

        [tool.towncrier]
        directory = "changelog.d"
        filename = "CHANGELOG.md"
        start_string = "<!-- towncrier release notes start -->\n"
        underlines = ["", "", ""]
        template = "changelog.d/changelog_template.jinja"
        title_format = "## [{version}](https://github.com/ansys/{repo-name}/releases/tag/v{version}) - {project_date}"
        issue_format = "[#{issue}](https://github.com/ansys/{repo-name}/pull/{issue})"

        [[tool.towncrier.type]]
        directory = "added"
        name = "Added"
        showcontent = true

        [[tool.towncrier.type]]
        directory = "changed"
        name = "Changed"
        showcontent = true

        [[tool.towncrier.type]]
        directory = "fixed"
        name = "Fixed"
        showcontent = true

        [[tool.towncrier.type]]
        directory = "dependencies"
        name = "Dependencies"
        showcontent = true

        [[tool.towncrier.type]]
        directory = "miscellaneous"
        name = "Miscellaneous"
        showcontent = true

  2. Create the changelog.d folder in the root of your repository, and create a file named changelog_template.jinja.
     Add the following lines to the ``jinja`` file:

    .. code:: jinja

        {% if sections[""] %}
        {% for category, val in definitions.items() if category in sections[""] %}

        ### {{ definitions[category]['name'] }}

        {% for text, values in sections[""][category].items() %}
        - {{ text }} {{ values|join(', ') }}
        {% endfor %}

        {% endfor %}
        {% else %}
        No significant changes.


        {% endif %}

  3. Add the following lines to the CHANGELOG.md file, replacing {repo-name} with the name of the repository:

    .. code:: md

        This project uses [*towncrier*](https://towncrier.readthedocs.io/) and the changes for the upcoming release can be found in <https://github.com/ansys/{repo-name}/tree/main/changelog.d/>.

        <!-- towncrier release notes start -->

  .. note::

      If CHANGELOG.md already has sections for previous releases, make sure to put the
      ``"towncrier release notes start"`` comment above the release sections. For example:

      .. code:: md

          <!-- towncrier release notes start -->

          ## [0.10.7](https://github.com/ansys/pymechanical/releases/tag/v0.10.7) - February 13 2024


  4. Update ``.github/workflows/label.yml`` and ``.github/workflows/ci_cd.yml`` to use the changelog action.

    Change the ``pull_request`` trigger at the top of each ``.yml`` file above, so it lists the pull request actions that cause the workflows to run.

    .. code:: yml

      on:
        pull_request:
          # opened, reopened, and synchronize are default for pull_request
          # edited - when PR title or body is changed
          # labeled - when labels are added to PR
          types: [opened, reopened, synchronize, edited, labeled]

    At the bottom of ``.github/workflows/label.yml``, add the following lines for the changelog action:

    .. code:: yml

        changelog-fragment:
          name: "Create changelog fragment"
          needs: [labeler]
          permissions:
            contents: write
            pull-requests: write
          runs-on: ubuntu-latest
          steps:
            - uses: ansys/actions/doc-changelog@feat/changelog-action
              with:
                token: ${{ secrets.GITHUB_TOKEN }}

  5. Steps 1-4 are only required for setup. Here are extra commands that could be helpful:

  Create a changelog file manually:

  .. code:: bash

      towncrier create -c "Added a feature!" 1.added.md

  .. note::

      "Added a feature!" adds the content of the file named 1.added.md.
      The number one in "1.added.md" is the pull request number and "added" is a subsection
      under the released version. For example, ``CHANGELOG.md`` would look like this if
      the above ``.md`` file only existed in changelog.d:

      .. code:: md

          ## [version](https://github.com/ansys/{repo-name}/releases/tag/v{version})

          ### Added

          - Added a feature! [#1](https://github.com/ansys/{repo-name}/pull/1)


  When you are ready to do a release for your repository, run the following command to
  update CHANGELOG.md with the files in changelog.d, replacing {version} with your
  release number. For example, 0.10.8 - do not include "v" in the version:

  .. code:: bash

      towncrier build --yes --version {version}

  If you want to update CHANGELOG.md, but keep the changelog.d files, run the following command:

  .. code:: bash

      towncrier build --keep --version {version}

  If you only want to preview the changelog, but don't want to make changes to CHANGELOG.md,
  run the following command:

  .. code:: bash

      towncrier build --keep --draft --version {version}


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
