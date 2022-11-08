Build actions
=============

The build actions allow for building artifacts for a Python library. These
artifacts include both source distribution files and wheels.


Build library action
--------------------
This action builds source and wheel artifacts for a Python library.

.. jinja:: build-library

    {{ inputs_table }}


Here is a code sample for using this action:

.. code-block:: yaml

    build-library:
      name: Build library
      runs-on: ubuntu-latest
      steps:
        - name: "Build library source and wheel artifacts"
          uses: pyansys/actions/build-library@main
          with:
            library-name: "ansys-<product>-<library>"


Build C-extension library action
--------------------------------
This action builds wheel artifacts for a Python library using
C-extension.

.. jinja:: build-ci-wheels

    {{ inputs_table }}


.. code-block:: yaml

    build-c-extension:
      name: Build a C-extension library
      runs-on: ${{ matrix.os }}
      strategy:
         matrix:
             os: [ubuntu-latest, windows-latest, macos-11]
      steps:
        - name: "Build a C-extension library wheel artifacts"
          uses: pyansys/actions/build-ci-library@main

