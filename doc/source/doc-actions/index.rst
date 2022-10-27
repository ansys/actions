Documentation actions
=====================

The documentation actions allow for building and deploying the documentation of
a PyAnsys project.

For using these actions, a project must use `Sphinx <https://www.sphinx-doc.org/en/master/>`_
as documentation parser.


Doc build action
----------------
This action builds the documentation of a PyAnsys project using the
`sphinx-build <https://www.sphinx-doc.org/en/master/man/sphinx-build.html>`_
command. 

Uses ``HTML``, ``PDF`` and ``JSON`` builders for generating the following
artifacts:

* ``documentation-html``: web-based documentation to be displayed in ``gh-pages``.
* ``documentation-pdf``: file-based documentation to be used in off-line tasks.
* ``documetation-json``: documentation to be consumed by Ansys developer's portal.

.. jinja:: doc-build

    {{ inputs_table }}

Code sample for using this action:

.. code-block:: yaml

    doc-build:
      name: "Building documentation"
      runs-on: ubuntu-latest
      needs: doc-style
      steps:
        - name: "Run Ansys documentation building action"
          uses: pyansys/actions/doc-build@main


Doc deploy dev action
---------------------
This action deploys de ``HTML`` documentation into ``gh-pages`` branch. It is
expected to be used after the :ref:`Doc build action`, since it looks for an
artifact named ``documentation-html``.

.. jinja:: doc-deploy-dev

    {{ inputs_table }}

Code sample for using this action:

.. code-block:: yaml

    doc-deploy-dev:
      name: "Deploy developers documentation"
      runs-on: ubuntu-latest
      needs: doc-build
      steps:
        - name: "Deploy the latest documentation"
          if: github.event_name == 'push'
          uses: pyansys/actions/doc-deploy-dev@main
          with:
              cname: "<library>.docs.pyansys.com"
              token: ${{ secrets.GITHUB_TOKEN }}


Doc deploy stable action
------------------------
This action deploys de ``HTML`` documentation into the ``release/`` directory of
the ``gh-pages`` branch. It is expected to be used after the :ref:`Doc build
action`, since it looks for an artifact named ``documentation-html``.

The logic behind this action is smart enough to identify the major and minor
versions of your stable documentation and generate a new folder named
``<MAJOR>.<MINOR>``. If this directory already exists, its content is override.

The ``release/`` directory is expected to contain a JSON file for versioning
mapping, as specified in `version switcher dropdown section
<https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/version-dropdown.html#version-switcher-dropdowns>`_
of the `PyData Sphinx Theme
<https://pydata-sphinx-theme.readthedocs.io/en/stable/index.html>`_.

In addition, the ``conf.py`` file is expected to contain the following keys and
values inside the ``html_theme_options``:

.. code-block:: python

    html_theme_options = {
        "switcher": {
            "json_url": "https://raw.githubusercontent.com/<owner>/<repository>/gh-pages/release/version_mapper.json",
            "version_match": "dev" if version.endswith("dev0") else version,
        },
        ...
    }

All previous logic allows to user from multi-version documentation history in
a PyAnsys project.

.. jinja:: doc-deploy-stable

    {{ inputs_table }}

Code sample for using this action:

.. code-block:: yaml

    doc-deploy-stable:
      name: "Deploy stable documentation"
      runs-on: ubuntu-latest
      needs: doc-build
      steps:
        - name: "Deploy the stable documentation"
          if: github.event_name == 'push' && contains(github.ref, 'refs/tags')
          uses: pyansys/actions/doc-deploy-stable@main
          with:
              cname: "<library>.docs.pyansys.com"
              token: ${{ secrets.GITHUB_TOKEN }}
