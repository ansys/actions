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
      runs-on: ${{ matrix.os }}
      strategy:
         matrix:
             os: [ubuntu-latest, windows-latest]
             python-version: ['3.7', '3.8', '3.9', '3.10']
      steps:
        - name: "Run pytest"
          uses: pyansys/actions/tests-pytest@v1
          with:
            pytest-markers: "-k 'mocked'"
            pytest-extra-args: "--cov=ansys.<library> --cov-report=term --cov-report=xml:.cov/coverage.xml --cov-report=html:.cov/html"
