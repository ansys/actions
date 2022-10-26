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

+-----------------+--------------------------------------------------------------+-----------+---------+----------------------------+
| Input           | Description                                                  | Required  | Type    | Default                    |
+=================+==============================================================+===========+=========+============================+
| python-version  | Desired Python version for Sphinx                            | false     | string  | '3.10'                     |
+-----------------+--------------------------------------------------------------+-----------+---------+----------------------------+
| sphinxopts      | Desired set of options to be passed to Sphinx builder        | false     | string  | '-j auto -W --keep-going'  |
+-----------------+--------------------------------------------------------------+-----------+---------+----------------------------+
| dependencies    | System dependencies required for building the documentation  | false     | string  | ''                         |
+-----------------+--------------------------------------------------------------+-----------+---------+----------------------------+
| requires-xvfb   | Whether to use X Virtual Frame Buffer for rendering the docs | false     | boolean | false                      |
+-----------------+--------------------------------------------------------------+-----------+---------+----------------------------+

Code sample for using this action:

.. code-block:: yaml

    doc-build:
      name: "Building documentation"
      runs-on: ubuntu-latest
      needs: doc-style
      steps:
        - name: "Run Ansys documentation building action"
          uses: pyansys/actions/doc-build@main
