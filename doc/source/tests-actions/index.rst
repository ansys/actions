Tests actions
=============

The tests actions allow to run the test suite for a Python library.


Test library action
--------------------
This action runs the test suite for a Python library. This action accepts
markers, options, and post arguments to be passed to pytest before executing the
test session.

.. jinja:: tests-pytest

    {{ inputs_table }}


Examples
++++++++

.. dropdown:: Testing library with different operating-systems and Python versions

    .. literalinclude:: examples/tests-pytest-basic.yml
       :language: yaml

.. dropdown:: Optimized testing library with different markers and arguments

    .. literalinclude:: examples/tests-pytest-optimized.yml
       :language: yaml
