Release actions
===============
Release actions provide for releasing the various artifacts of a Python library.

These actions assume that you have used the :ref:`Documentation actions`
and the :ref:`Build actions`. The reason is that the artifacts generated during these
actions are the ones to be released.


Release PyPI private action
---------------------------

.. jinja:: release-pypi-private
    :file: _templates/action.rst.jinja

Release PyPI test action
------------------------

.. jinja:: release-pypi-test
    :file: _templates/action.rst.jinja

Release PyPI public action
--------------------------

.. jinja:: release-pypi-public
    :file: _templates/action.rst.jinja

Release GitHub action
---------------------

.. jinja:: release-github
    :file: _templates/action.rst.jinja

Release PyPI template
---------------------

The following code assumes that a `build-library` job has already created library sources
and wheel artifacts using the `PACKAGE_NAME` environment variable. Also, the job's 
`skip-existing` input indicates that files that already exist are not uploaded again.

.. code::yaml

    release-pypi:
    name: "Release to PyPI with trusted publisher approach"
    runs-on: ubuntu-latest
    needs: [build-library]
    # Specifying a GitHub environment is optional but strongly encouraged
    environment: release
    permissions:
        # IMPORTANT: This permission is mandatory for trusted publishing.
        id-token: write
    if: github.event_name == 'push' && contains(github.ref, 'refs/tags')
    steps:
      - name: "Download the library artifacts from build-library step"
        uses: actions/download-artifact@v4
        with:
            name: ${{ env.PACKAGE_NAME }}-artifacts
            path: ${{ env.PACKAGE_NAME }}-artifacts

      - name: "Display the structure of downloaded files"
        shell: bash
        run: ls -R

      - name: "Upload artifacts to PyPI using trusted publisher approach"
        uses: pypa/gh-action-pypi-publish@v1.12.4
        with:
            repository-url: "https://upload.pypi.org/legacy/"
            print-hash: true
            packages-dir: ${{ env.PACKAGE_NAME }}-artifacts
            skip-existing: false

When testing the release process, you can update the repository URL as
follows:

.. code::yaml

        uses: pypa/gh-action-pypi-publish@v1.12.4
        with:
            repository-url: "https://test.pypi.org/legacy/"
            print-hash: true
            packages-dir: ${{ env.PACKAGE_NAME }}-artifacts
            skip-existing: false
