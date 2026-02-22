Licenses actions
================

Licenses actions verify that any dependency used by a Python library uses
PyAnsys authorized open source licenses. 


Check licenses action
---------------------

This action allows to verify that the project's dependencies only contain valid
licenses.

.. jinja:: check-licenses

    .. grid:: 1 1 1 2
        :gutter: 2
    
        .. grid-item-card:: :octicon:`codescan-checkmark` Accepted third party licenses
    
            {% for license in accepted_licenses %}
            * {{ license }}
            {% endfor %}
    
        .. grid-item-card:: :octicon:`package` Ignored packages
    
            {% for package in ignored_packages %}
            * {{ package }}
            {% endfor %}

.. admonition:: Projects requiring additional licenses or packages

    If a certain project requires a license or package that is not supported,
    `open an issue <https://github.com/pyansys/actions/issues>`_ in the
    `official pyansys/actions repository
    <https://github.com/pyansys/actions>`_. For additional support, please
    contact the `PyAnsys support <mailto:support@pyansys.com>`_.

.. jinja:: check-licenses

    {{ inputs_table }}

    Examples
    ++++++++

    {% for filename, title in examples %}
    .. dropdown:: {{ title }}
       :animate: fade-in

        .. literalinclude:: examples/{{ filename }}
           :language: yaml

    {% endfor %}




