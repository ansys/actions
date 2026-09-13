Documentation actions
=====================

Documentation actions build and deploy the documentation of
a PyAnsys project.

To use these actions, a project must use `Sphinx <https://www.sphinx-doc.org/en/master/>`_
as documentation parser.


Doc build action
----------------

.. jinja:: doc-build

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


Doc deploy dev action
---------------------

.. jinja:: doc-deploy-dev

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


Doc deploy stable action
------------------------

.. jinja:: doc-deploy-stable

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
