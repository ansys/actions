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
          uses: pyansys/actions/build-library@v1
          with:
            library-name: "ansys-<product>-<library>"


here is a code for using this action

Build wheelhouse action
-----------------------
This action builds the wheelhouse for a Python library and publishes them as
artifacts.

.. jinja:: build-wheelhouse

    {{ inputs_table }}

Here is a code sample for using this action:

.. code-block:: yaml

    build-wheelhouse:
      name: Build the wheelhouse of the Python library
      runs-on: ${{ matrix.os }}
      strategy:
         matrix:
             os: [ubuntu-latest, windows-latest]
             python-version: ['3.7', '3.8', '3.9', '3.10']
      steps:
        - name: "Build a wheelhouse of the Python library"
          uses: pyansys/actions/build-wheelhouse@v1
          with:
            library-name: "<ansys-product-library>"
            library-namespace: "<ansys.product.libray>"
            operating-system: ${{ matrix.os }}
            python-version: ${{ matrix.python-version }}


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
          uses: pyansys/actions/build-ci-library@v1

