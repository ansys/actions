Housekeeping actions
====================
Housekeeping actions provide for general repository operations such as package cleanup.


Package cleanup of untagged versions
------------------------------------

.. jinja:: hk-package-clean-untagged

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


Package cleanup excluding certain versions
------------------------------------------

.. jinja:: hk-package-clean-except

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

