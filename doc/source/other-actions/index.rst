Other actions
=============
Other actions that provide additional checks and capabilities.


Check branch name is aligned to PyAnsys branch naming style
-----------------------------------------------------------

.. jinja:: check-branch-name

    {{ description }}

    Examples
    ++++++++

    {% for filename, title in examples %}
    .. dropdown:: {{ title }}
       :animate: fade-in

       .. literalinclude:: examples/{{ filename }}
          :language: yaml

    {% endfor %}


Check pull request title follows conventional commits standard
--------------------------------------------------------------

.. jinja:: check-pr-conventional-name

    {{ description }}

    Examples
    ++++++++

    {% for filename, title in examples %}
    .. dropdown:: {{ title }}
       :animate: fade-in

       .. literalinclude:: examples/{{ filename }}
          :language: yaml

    {% endfor %}

