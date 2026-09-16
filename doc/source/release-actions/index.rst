Release actions
===============
Release actions provide for releasing the various artifacts of a Python library.

These actions assume that you have used the :ref:`Documentation actions`
and the :ref:`Build actions`. The reason is that the artifacts generated during these
actions are the ones to be released.

Release workflow setup
----------------------

See :ref:`release_workflow_setup` for typical release workflow setups, grouped according
to the different modes for generating the changelog during a release.


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

.. toctree::
    :hidden:

    release-workflow
