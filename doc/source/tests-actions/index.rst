Tests actions
=============

The tests actions allow to run the test suite for a Python library.


Test library action
--------------------
This action runs the test suite for a Python library. This action accepts
markers, options, and post arguments to be passed to pytest before executing the
test session.

.. jinja:: tests-pytest

    {{ inputs_table }}


Here is a code sample for using this action:

.. code-block:: yaml

    tests:
      name: "Test library"
      runs-on: ubuntu-latest
      strategy:
         matrix:
             os: [ubuntu-latest, windows-latest]
             python-version: ['3.7', '3.8', '3.9', '3.10']
      steps:
        - name: "Run pytest"
          uses: pyansys/actions/tests-pytest@main
          with:
            pytest-markers: "-k 'mocked'"
            pytest-options: "--cov"
