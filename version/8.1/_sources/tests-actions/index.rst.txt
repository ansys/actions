Tests actions
=============

The tests actions allow to run the test suite for a Python library.


Test library action
--------------------
This action runs the test suite for a Python library. This action accepts
markers, options, and post arguments to be passed to pytest before executing the
test session.

.. jinja:: tests-pytest
    :file: _templates/action.rst.jinja
