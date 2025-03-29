Build actions
=============

The build actions allow for building artifacts for a Python library. These
artifacts include both source distribution files and wheels.


Build library action
--------------------
This action builds source and wheel artifacts for a Python library.

.. jinja:: build-library

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
This action builds the wheelhouse for a Python library and publishes them as
artifacts.

.. jinja:: build-wheelhouse

    {{ inputs_table }}

    Examples
    ++++++++

    {% for filename, title in examples %}
    .. dropdown:: {{ title }}
       :animate: fade-in

        .. literalinclude:: examples/{{ filename }}
           :language: yaml

    {% endfor %}


Build C-extension library action
--------------------------------
This action builds wheel artifacts for a Python library using
C-extension.

.. jinja:: build-ci-wheels

    {{ inputs_table }}

    Examples
    ++++++++

    {% for filename, title in examples %}
    .. dropdown:: {{ title }}
       :animate: fade-in

        .. literalinclude:: examples/{{ filename }}
           :language: yaml

    {% endfor %}

