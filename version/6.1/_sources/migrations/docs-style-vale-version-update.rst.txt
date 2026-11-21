.. _docs_style_vale_update:

Doc-style action - migrating from Vale ``2.X`` to ``3.X``
=========================================================

When migrating ``ansys/actions/doc-style`` from ``v5`` to higher versions, the default Vale version is upgraded to ``v3``.
Certain changes must be made to the repository to ensure that the ``doc-style`` action performs without issues.
Additionally, it is possible to use ``ansys/actions`` older than ``v5`` while utilizing Vale ``v3``
as input for the ``doc-style`` action like below.

.. code:: yaml

    doc-style:
      name: Documentation Style Check
      runs-on: ubuntu-latest
      steps:
        - name: PyAnsys documentation style checks
          uses: ansys/actions/doc-style@v5
          with:
            token: ${{ secrets.GITHUB_TOKEN }}
            vale-version: "3.4.1"

In any of the preceding conditions, there are two mandatory changes and one optional (depending on
the repository setup) needs to implemented:

1. Update ``Vocab/ANSYS`` path

   In order to comply with the requirements of Vale ``v3``, it is necessary to update the vocabularies
   path under the ``doc/styles`` directory. Specifically, the default vocabularies path should be modified from
   ``Vocab/ANSYS`` to ``config/vocabularies/ANSYS``. This adjustment ensures that Vale can locate the required vocabulary files.

   .. note:: Update ``.gitignore``

      If your repository has ``.gitignore`` files under ``styles`` folder, please update them according to vocabularies changes

2. Turn off ``Vale.Terms``

   Locate the section in your ``doc/.vale.ini`` file where styles are applied.
   Add ``Vale.Terms = NO`` under the section where styles are applied, typically marked with ``[*.{rst}]``.

   .. code:: ini

      [*.{rst}]
      BasedOnStyles = Vale, Google
      Vale.Terms = NO

3. Update ``codespell`` hook

   If your repository includes a ``codespell`` hook in the ``.pre-commit-config.yaml`` file,
   utilizing the ``accept.txt`` file, it necessitates modification to reflect the new path
   as provided below.

   .. code:: yaml

     - repo: https://github.com/codespell-project/codespell
       rev: v2.2.6
       hooks:
       - id: codespell
         args: ["--ignore-words", "doc/styles/config/vocabularies/ANSYS/accept.txt"]


Finally, verify that the ``doc-style`` action is functioning correctly with the latest changes applied.
Run the action and ensure that the documentation style checks are performed without any issues.