Licenses actions
================

The ``pyansys/check-licenses`` action allows to verify that the project's dependencies
only contain valid licenses.

The valid licenses are defined in the ``accepted-licenses.txt``. Moreover, an additional txt
file ``ignored-packages.txt`` contains a list of packages that are trusted but may not have a
valid license associated.

Use of the check-licenses action
--------------------------------

This acction accepts the following inputs.

.. jinja:: check-licenses

    {{ inputs_table }}

Here is a code sample for using this action:

.. code-block:: yaml

    check-licenses:
    name: "Check dependencies' licenses"
    runs-on: ubuntu-latest
    steps:
      - name: "PyAnsys check_licenses action"
          uses: pyansys/actions/check-licenses@main
          with:
            python-version: ${{ env.MAIN_PYTHON_VERSION }}

Update txt files
----------------

As mentioned before, the two txt files ``accepted-licenses.txt`` and ``ignored-packages.txt`` define the
valid licenses and ignored packages. If a certain repository requires a different license or packages
that is not included in the original list, a PR can be proposed to ``pyansys/actions`` in order to
modify these txt files as needed. When doing that, two considerations have to be taken into account:

- Changes must only include additions to the files, so they contain the complete list of licenses used
  across the entire PyAnsys ecosystem.
- The content of both files has to be alphabetically sorted.
