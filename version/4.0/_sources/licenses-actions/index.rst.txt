Licenses actions
================

Licenses actions verify that any dependency used by a Python library uses
PyAnsys authorized open source licenses.


Check licenses action
---------------------

.. jinja:: check-licenses

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




