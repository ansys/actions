PyAnsys Actions
===============
|pyansys| |MIT|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

A repository containing a collection of `GitHub Workflows`_ to be reused by
projects in the PyAnsys ecosystem.


Available actions
-----------------
This section collects all the available actions. If you encounter any issues
when reusing those in your project, please `open an issue
<https://github.com/pyansys/actions/issues>`_. 

Code style action
^^^^^^^^^^^^^^^^^
This action evaluates the code quality of your project by using `pre-commit
<https://pre-commit.com/>`_. It is assumed that your project contains a
``.pre-comit-config.yaml`` file in the base root directory.

+-----------------+----------------------------------------+-----------+---------+----------+
| Input           | Description                            | Required  | Type    | Default  |
+=================+========================================+===========+=========+==========+
| python-version  | Desired Python version for pre-commit  | False     | string  | '3.10'   |
+-----------------+----------------------------------------+-----------+---------+----------+

Code sample for using this action:

.. code-block:: yaml

    code-style:
      name: Code style
      runs-on: ubuntu-latest
      steps:
        - name: "Run PyAnsys code style checks"
          uses: pyansys/actions/code-style@main


Doc style action
^^^^^^^^^^^^^^^^
This action evaluates the documentation quality of your project by using `Vale
<https://vale.sh/>`_. It is assumed that your project contains a
``.pre-comit-config.yaml`` file in the base root directory. A token is expected
as input for Vale to indicate quality errors by making comments. This token can
be the ``${{ secrets.GITHUB_TOKEN }}`` one.


+--------------+--------------------------------------+-----------+---------+------------------+
| Input        | Description                          | Required  | Type    | Default          |
+==============+======================================+===========+=========+==================+
| vale-config  | Path to the Vale configuration file  | False     | string  | 'doc/.vale.ini'  |
| token        | Required token for Vale commenter    | True      |         |                  |
+--------------+--------------------------------------+-----------+---------+------------------+

Code sample for using this action:

.. code-block:: yaml

    doc-style:
      name: Doc style
      runs-on: ubuntu-latest
      steps:
        - name: "Run Ansys documentation style checks"
          uses: pyansys/actions/doc-style@main
          with:
            token: ${{ secrets.GITHUB_TOKEN }}


.. LINKS AND REFERENCES

.. _GitHub workflows: https://docs.github.com/en/actions/using-workflows/about-workflows
.. _pyansys: https://docs.pyansys.com/
