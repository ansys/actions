Release actions
===============
The release actions allow for releasing the various artifacts of a Python library.

These set of actions assume that you have used the :ref:`Documentation actions`
and the :ref:`Build actions`. The reason is that the artifacts generated during these
actions are the ones to be released.


Release private action
----------------------
This action allows for deploying all Python library artifacts into the `Ansys
private PyPI index
<https://dev.docs.pyansys.com/how-to/releasing.html#publish-privately-on-pypi>`_.

The ``PYANSYS_PYPI_PRIVATE_PAT`` token is required for successfully executing
this action.


.. jinja:: release-private

    {{ inputs_table }}

Code sample for using this action:

.. code-block:: yaml

    release-private:
      name: "Release to private PyPI"
      runs-on: ubuntu-latest
      needs: [build-library]
      steps:
        - name: "Release to the private PyPI repository"
          if: github.event_name == 'push' && contains(github.ref, 'refs/tags')
          uses: pyansys/actions/release-private@main
          with:
            library-name: "ansys-<product>-<library"
            twine-token: ${{ secrets.PYANSYS_PYPI_PRIVATE_PAT }}


Release public action
---------------------
This action allows for deploying all Python library artifacts into the public
`PyPI index <https://pypi.org/>`_.

Similarly to :ref:`Release private action`, the ``PYPI_TOKEN`` is required.


.. jinja:: release-public

    {{ inputs_table }}

Code sample for using this action:

.. code-block:: yaml

    release-public:
      name: "Release to public PyPI"
      runs-on: ubuntu-latest
      needs: [build-library]
      steps:
        - name: "Release to the public PyPI repository"
          if: github.event_name == 'push' && contains(github.ref, 'refs/tags')
          uses: pyansys/actions/release-public@main
          with:
            library-name: "ansys-<product>-<library"
            twine-token: ${{ secrets.PYPI_TOKEN }}


Release GitHub action
---------------------
This action allows for deploying all Python library artifacts into the `GitHub
releases section
<https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository>`_
of a repository.

.. jinja:: release-github

    {{ inputs_table }}

Code sample for using this action:

.. code-block:: yaml

    release-gitub:
      name: "Release to GitHub"
      runs-on: ubuntu-latest
      needs: [build-library]
      steps:
        - name: "Release to GitHub"
          if: github.event_name == 'push' && contains(github.ref, 'refs/tags')
          uses: pyansys/actions/release-github@main
          with:
            library-name: "ansys-<product>-<library"

