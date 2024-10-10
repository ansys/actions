Style actions
=============
Style actions verify code and documentation quality compliance
with PyAnsys guidelines.

To use these actions, a project must use `pre-commit
<https://pre-commit.com>`_ and `Vale <https://vale.sh>`_. For help
implementing these tools, send an email to `pyansys.support@ansys.com
<mailto:pyansys.support@ansys.com>`_.

Code style action
-----------------
This action evaluates the code quality of your project by using `pre-commit`_. It is assumed that your project contains a
``.pre-commit-config.yaml`` file in the root directory.

.. jinja:: code-style

    {{ inputs_table }}

Here is a code sample for using this action:

.. code-block:: yaml

    code-style:
      name: Code style
      runs-on: ubuntu-latest
      steps:
        - name: "Run PyAnsys code style checks"
          uses: pyansys/actions/code-style@v1


Doc style action
----------------
This action evaluates the documentation quality of your project by using
`Vale`_. It assumes that Vale's configuration file is stored in
``doc/.vale.ini``. A token is expected as input for Vale to indicate quality
errors by making comments. This token can be the ``${{ secrets.GITHUB_TOKEN }}``
one.

+--------------+--------------------------------------+-----------+---------+------------------+
| Input        | Description                          | Required  | Type    | Default          |
+==============+======================================+===========+=========+==================+
| vale-config  | Path to the Vale configuration file  | False     | string  | 'doc/.vale.ini'  |
+--------------+--------------------------------------+-----------+---------+------------------+
| token        | Required token for Vale commenter    | True      |         |                  |
+--------------+--------------------------------------+-----------+---------+------------------+

Here is a code sample for using this action:

.. code-block:: yaml

    doc-style:
      name: Doc style
      runs-on: ubuntu-latest
      steps:
        - name: "Run Ansys documentation style checks"
          uses: pyansys/actions/doc-style@v1
          with:
            token: ${{ secrets.GITHUB_TOKEN }}

