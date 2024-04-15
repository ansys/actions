.. _docs_style_vale_update:

Doc-style action - vale update
==============================

When migrating ``ansys/actions/doc-style`` from v5 to higher versions, vale version is upgraded to ``v3``.
Certain changes must be made to the repository to ensure that the ``doc-style`` action performs without issues.
Additionally, it is possible to use ansys actions older than version 5 while utilizing vale version 3
or above as input for the ``doc-style`` action like below.

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

In any of the above two conditions there  are two changes needs to implemented:

1. Update **vocabularies** path

   In order to comply with the requirements of Vale version 3 or above, it is necessary to update the vocabularies
   path under the ``doc/styles`` directory. Specifically, the default vocabularies path should be modified from
   ``Vocab/ANSYS`` to ``config/vocabularies/ANSYS``. This adjustment ensures that Vale can locate the required vocabulary files.

   .. note:: Update ``.gitignore``

    If your repository has ``.gitignore`` files under ``styles`` folder, please update them according to vocabularies changes

2. Turn off **Vale Terms**

   Locate the section in your ``doc/.vale.ini`` file where styles are applied.
   Add ``Vale.Terms = NO`` under the section where styles are applied, typically marked with ``[*.{rst}]``.

   .. code:: ini

    [*.{rst}]
    BasedOnStyles = Vale, Google
    Vale.Terms = NO


Finally, verify that the ``doc-style`` action is functioning correctly with the latest changes applied.
Run the action and ensure that the documentation style checks are performed without any issues