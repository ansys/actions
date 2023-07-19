Build actions
=============

The build actions allow for building artifacts for a Python library. These
artifacts include both source distribution files and wheels.


Build library action
--------------------

.. jinja:: build-library

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


Build wheelhouse action
-----------------------

.. jinja:: build-wheelhouse

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


Build CI wheels action
----------------------

.. jinja:: build-ci-wheels

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

