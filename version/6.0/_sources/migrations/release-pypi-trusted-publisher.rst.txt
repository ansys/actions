.. _release_pypi_trusted_publisher:

Release to PyPI as a trusted publisher
--------------------------------------

Starting on ``ansys/actions`` version 6, repository maintainers can benefit from the
`Trusted Publishers release to PyPI <https://docs.pypi.org/trusted-publishers/>`_ approach.

Traditionally, projects have made use of the `PyPI API token <https://pypi.org/help/#apitoken>`_ to
upload packages to PyPI. This approach is still supported, but it is recommended to use the
Trusted Publishers approach when possible. If you are a repository maintainer and you want to
release to PyPI as a trusted publisher, follow these steps:

#. Contact the `PyAnsys Core Team <mailto:pyansys.core@ansys.com>`_ to request your project
   to be added to the list of authorized repositories to release as a trusted publisher.

#. (Optional) Create a dedicated ``release`` environment on your GitHub repository. This step is
   optional, but it is strongly encouraged. To create a new environment, go to the
   `Environments <https://docs.github.com/en/actions/deployment/targeting-different-environments/using-environments-for-deployment>`_
   documentation. Contact the `PyAnsys Core Team`_ in case of doubts.

#. Adapt your ``release`` section in your workflow as follows:

   .. code-block:: yaml

      release:
        name: Release project
        if: ${{ github.event_name == 'push' && contains(github.ref, 'refs/tags') }}
        needs: [package]
        runs-on: ubuntu-latest
        # Specifying a GitHub environment is optional, but strongly encouraged
        environment: release
        permissions:
          id-token: write
          contents: write
        steps:
          - name: Release to the public PyPI repository
            uses: ansys/actions/release-pypi-public@v6
            with:
              library-name: ${{ env.PACKAGE_NAME }}
              use-trusted-publisher: true

          - name: Release to GitHub
            uses: ansys/actions/release-github@v6
            with:
              library-name: ${{ env.PACKAGE_NAME }}

