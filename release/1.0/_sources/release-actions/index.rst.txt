Release actions
===============
Release actions provide for releasing the various artifacts of a Python library.

These actions assume that you have used the :ref:`Documentation actions`
and the :ref:`Build actions`. The reason is that the artifacts generated during these
actions are the ones to be released.


Release PyPI private action
---------------------------
This action deploys all Python library artifacts into the `Ansys
private PyPI index
<https://dev.docs.pyansys.com/how-to/releasing.html#publish-privately-on-pypi>`_.

The ``PYANSYS_PYPI_PRIVATE_PAT`` token is required for successfully executing
this action.


.. jinja:: release-pypi-private

    {{ inputs_table }}

Here is a code sample for using this action:

.. code-block:: yaml

    release-pypi-private:
      name: "Release to private PyPI"
      runs-on: ubuntu-latest
      needs: [build-library]
      steps:
        - name: "Release to the private PyPI repository"
          if: github.event_name == 'push' && contains(github.ref, 'refs/tags')
          uses: pyansys/actions/release-pypi-private@v1
          with:
            library-name: "ansys-<product>-<library"
            twine-username: "__token__"
            twine-token: ${{ secrets.PYANSYS_PYPI_PRIVATE_PAT }}

Release PyPI test action
------------------------
This action deploys all Python library artifacts into the `Test PyPI index
<https://test.pypi.org>`_ index.

The ``PYANSYS_PYPI_TEST_PAT`` token is required for successfully executing
this action.

.. jinja:: release-pypi-test

    {{ inputs_table }}

Here is a code sample for using this action:

.. code-block:: yaml

    release-pypi-test:
      name: "Release to test PyPI"
      runs-on: ubuntu-latest
      needs: [build-library]
      steps:
        - name: "Release to the test PyPI repository"
          if: github.event_name == 'push' && contains(github.ref, 'refs/tags')
          uses: pyansys/actions/release-pypi-test@v1
          with:
            library-name: "ansys-<product>-<library"
            twine-username: "__token__"
            twine-token: ${{ secrets.PYANSYS_PYPI_TEST_PAT }}

Release PyPI public action
--------------------------
This action deploys all Python library artifacts into the public
`PyPI index <https://pypi.org/>`_.

Similarly to :ref:`Release PYPI private action`, the ``PYPI_TOKEN`` is required.


.. jinja:: release-pypi-public

    {{ inputs_table }}

Here is a code sample for using this action:

.. code-block:: yaml

    release-pypi-public:
      name: "Release to public PyPI"
      runs-on: ubuntu-latest
      needs: [build-library]
      steps:
        - name: "Release to the public PyPI repository"
          if: github.event_name == 'push' && contains(github.ref, 'refs/tags')
          uses: pyansys/actions/release-pypi-public@v1
          with:
            library-name: "ansys-<product>-<library"
            twine-username: "__token__"
            twine-token: ${{ secrets.PYPI_TOKEN }}


Release GitHub action
---------------------
This action deploys all Python library artifacts into the `GitHub
releases section
<https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository>`_
of a repository.

.. jinja:: release-github

    {{ inputs_table }}

Here is a code sample for using this action:

.. code-block:: yaml

    release-gitub:
      name: "Release to GitHub"
      runs-on: ubuntu-latest
      needs: [build-library]
      steps:
        - name: "Release to GitHub"
          if: github.event_name == 'push' && contains(github.ref, 'refs/tags')
          uses: pyansys/actions/release-github@v1
          with:
            library-name: "ansys-<product>-<library"

