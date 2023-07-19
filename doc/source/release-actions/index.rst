Release actions
===============
Release actions provide for releasing the various artifacts of a Python library.

These actions assume that you have used the :ref:`Documentation actions`
and the :ref:`Build actions`. The reason is that the artifacts generated during these
actions are the ones to be released.


Release PyPI private action
---------------------------

.. jinja:: release-pypi-private

    {{ url }}

    {{ description }}

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

.. jinja:: release-pypi-test

    {{ url }}

    {{ description }}

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

.. jinja:: release-pypi-public

    {{ url }}

    {{ description }}

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

.. jinja:: release-github

    {{ url }}

    {{ description }}

    {{ inputs_table }}

    Examples
    ++++++++

    {% for filename, title in examples %}
    .. dropdown:: {{ title }}
       :animate: fade-in

       .. literalinclude:: examples/{{ filename }}
          :language: yaml

    {% endfor %}


