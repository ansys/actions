Release actions
===============
Release actions provide for releasing the various artifacts of a Python library.

These actions assume that you have used the :ref:`Documentation actions`
and the :ref:`Build actions`. The reason is that the artifacts generated during these
actions are the ones to be released.


Release PyPI private action
---------------------------
This action deploys all Python library artifacts into the `Ansys
private PyPI index
<https://dev.docs.pyansys.com/how-to/releasing.html#publish-privately-on-pypi>`_.

The ``PYANSYS_PYPI_PRIVATE_PAT`` token is required for successfully executing
this action.


.. jinja:: release-pypi-private

    {{ inputs_table }}

    Examples
    ++++++++

    {% for filename, title in examples %}
    .. dropdown:: {{ title }}
       :animate: fade-in

        .. literalinclude:: examples/{{ filename }}
           :language: yaml

    {% endfor %}


Release PyPI test action
------------------------
This action deploys all Python library artifacts into the `Test PyPI index
<https://test.pypi.org>`_ index.

The ``PYANSYS_PYPI_TEST_PAT`` token is required for successfully executing
this action.

.. jinja:: release-pypi-test

    {{ inputs_table }}

    Examples
    ++++++++

    {% for filename, title in examples %}
    .. dropdown:: {{ title }}
       :animate: fade-in

        .. literalinclude:: examples/{{ filename }}
           :language: yaml

    {% endfor %}

Release PyPI public action
--------------------------
This action deploys all Python library artifacts into the public
`PyPI index <https://pypi.org/>`_.

Similarly to :ref:`Release PYPI private action`, the ``PYPI_TOKEN`` is required.


.. jinja:: release-pypi-public

    {{ inputs_table }}

    Examples
    ++++++++

    {% for filename, title in examples %}
    .. dropdown:: {{ title }}
       :animate: fade-in

        .. literalinclude:: examples/{{ filename }}
           :language: yaml

    {% endfor %}


Release GitHub action
---------------------
This action deploys all Python library artifacts into the `GitHub
releases section
<https://docs.github.com/en/repositories/releasing-projects-on-github/managing-releases-in-a-repository>`_
of a repository.

.. jinja:: release-github

    {{ inputs_table }}

    Examples
    ++++++++

    {% for filename, title in examples %}
    .. dropdown:: {{ title }}
       :animate: fade-in

        .. literalinclude:: examples/{{ filename }}
           :language: yaml

    {% endfor %}


