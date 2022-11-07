Tests actions
=============

The tests actions allow for running the test suite for a Python library.


Build library action
--------------------
This action runs the test suite for a Python library. This action accepts
markers, options and post arguments to be passed to pytest before executing the
test session.

.. jinja:: tests-pytest

    {{ inputs_table }}


Here is a code sample for using this action:

.. code-block:: yaml

    tests:
      name: Build library
      runs-on: ubuntu-latest
      steps:
        - name: "Run pytest"
          uses: pyansys/actions/tests-pytest@main
          with:
            pytest-markers: "-k 'mocked'"
            pytest-options: "--cov"
