.. readme_common_begins
Ansys actions
=============
|ansys| |CI-CD| |MIT|

.. |ansys| image:: https://img.shields.io/badge/Ansys-ffc107.svg?labelColor=black&logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://actions.docs.ansys.com/
   :alt: Ansys

.. |CI-CD| image:: https://github.com/ansys/actions/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/ansys/actions/actions/workflows/ci_cd.yml
   :alt: CI-CD

.. |MIT| image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://opensource.org/blog/license/mit
   :alt: MIT

A repository containing a collection of `GitHub Workflows
<https://docs.github.com/en/actions/using-workflows/about-workflows>`_ to be
reused by projects in the Ansys ecosystem.

.. readme_common_ends

For more information on available actions and how to use them, see
`actions.docs.ansys.com <https://actions.docs.ansys.com>`_ .


Recommended workflow strategy
=============================

The different actions provided by `ansys/actions
<https://github.com/ansys/actions>`_ can be used to create a simple but
effective workflow.

The following lines describe the suggested workflows for various events, such as
pushing a new commit to a pull request, merging a commit to the main branch of a
repository, and performing a new release. Each image showcases the distinct job
steps declared in a YML file. Jobs highlighted in green signify that they
execute, while those with a grey background indicate that they do not execute.

For additional in-depth information refer to the poster `CI/CD pipelines for
scientists <https://scipy2023.pyansys.com/ci_cd.pdf>`_.

|

**Recommended workflow when pushing a new commit to a pull-request**

This workflow is recommended to ensure that the code ready to be merged is
compliant with the project style, its code integrity, and that it is capable of
successfully generating all the desired library artifacts.

.. image:: https://github.com/ansys/actions/blob/main/doc/source/_static/ci_cd_pr.png

|

**Recommended workflow when merging a new commit to the main branch of a repository**

This workflow is similar to the one for validating new code contributions in a
pull-request, but it also deploys the development documentation as new changes
were introduced in the main development branch.

.. image:: https://github.com/ansys/actions/blob/main/doc/source/_static/ci_cd_main.png

|

**Recommended workflow when performing a new release**

This workflow outlines the recommended steps for performing a new software
release, ensuring a smooth and well-documented process by deploying
the stable documentation at the end of the workflow.

.. image:: https://github.com/ansys/actions/blob/main/doc/source/_static/ci_cd_release.png
