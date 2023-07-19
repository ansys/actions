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
   :target: https://opensource.org/licenses/MIT
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
effective workflows.

The following lines suggest the recommended workflows for different events
including pushing a new commit to a pull-request, merging a commit to the main
branch of a repository, and performing a new release. Each image contains the
different job steps declared in a YML file. Jobs colored with green color
execute whereas jobs colored with a grey background do not execute.

|

**Recommended workflow when pushing a new commit to a pull-request**
This workflow is recommended to ensure that the code ready to be merged is
compliant with the project style, its code integrity, and that it is capable of
successfully generating all the desired library artifacts.

.. image:: https://github.com/ansys/actions/blob/doc/readme/doc/source/_static/ci_cd_pr.png

|

**Recommended workflow when merging a new commit to the main branch of a repository**
This workflow is similar to the one for validating new code contributions in a
pull-request, but it also deploys the development documentation as new changes
were introduced in the main development branch.

.. image:: https://github.com/ansys/actions/blob/doc/readme/doc/source/_static/ci_cd_main.png

|

**Recommended workflow when performing a new release**
This workflow outlines the recommended steps for performing a new software
release, ensuring a smooth and well-documented process by deploying
the stable documentation at the end of the workflow.

.. image:: https://github.com/ansys/actions/blob/doc/readme/doc/source/_static/ci_cd_release.png


