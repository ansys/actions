.. _release_pypi_trusted_publisher:

Release to PyPI as a trusted publishers
---------------------------------------

The trusted publisher feature allows projects to release packages to PyPI
without the need for a PyPI API token. This feature is available for projects
deploying from GitHub Actions.

Due to its security implications, the trusted publisher feature can not be used
with composite actions. Therefore, users of Ansys Actions must declare their
own release job.

#. Contact the `PyAnsys Core Team <mailto:pyansys.core@ansys.com>`_ to request
   authorization to release as a trusted publisher.

#. Adapt your ``release`` job in as follows:

   .. code-block:: yaml

      release:
        name: Release project
        if: ${{ github.event_name == 'push' && contains(github.ref, 'refs/tags') }}
        needs: build-library
        runs-on: ubuntu-latest
        # INFO: Specifying a GitHub environment is optional but encouraged
        environment: release
        # INFO: Trusted publishers require these permissions
        permissions:
          id-token: write
          contents: write
        steps:

          - name: "Download the library artifacts from build-library step"
            uses: actions/download-artifact@cc203385981b70ca67e1cc392babf9cc229d5806 # v4.1.9
            with:
              name: ${{ env.PACKAGE_NAME }}-artifacts
              path: ${{ env.PACKAGE_NAME }}-artifacts

          - name: "Upload artifacts to PyPI using trusted publisher"
            uses: pypa/gh-action-pypi-publish@76f52bc884231f62b9a034ebfe128415bbaabdfc # v1.12.4
            with:
              repository-url: "https://upload.pypi.org/legacy/"
              print-hash: true
              packages-dir: ${{ env.PACKAGE_NAME }}-artifacts
              skip-existing: false

..
   Links and references

.. _PyAnsys Core Team: mailto:pyansys.core@ansys.com
