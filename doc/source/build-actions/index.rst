Build actions
=============

The build actions allow for building artifacts for a Python library. These
artifacts include both source distribution files and wheels.


Build library action
--------------------
This action allows for building source and wheel artifacts for a Python library.

.. jinja:: build-library

    {{ inputs_table }}


Code sample for using this action:

.. code-sample:: yaml

    code-style:
  name: Code style
  runs-on: ubuntu-latest
  steps:
    - name: "Run PyAnsys code style checks"
      uses: pyansys/actions/build-library@main
      with:
        library-name: "ansys-<product>-<library"
