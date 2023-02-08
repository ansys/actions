Housekeeping actions
====================
Housekeeping actions provide for general repository operations such as package cleanup.


Package cleanup of untagged versions
------------------------------------
This action cleans up all the untagged package versions published in
`ghcr.io <https://ghcr.io/>`_. This is useful for scheduled package uploads that
leave untagged versions on GitHub's package registry.

Requirements for running this action:

* A token with **write package permissions** is needed.
* Target package must belong to the repository using this action.



.. jinja:: hk-package-clean-untagged

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

This action cleans up **all** the package versions published in
`ghcr.io <https://ghcr.io/>`_ **except for a specific list of tags**. This is useful for scheduled

package uploads that keep updating a tag while leaving other older tags behind.


Requirements for running this action:

* A token with **write package permissions** is needed.
* List of excluding tags, such as ``latest, latest-unstable``.
* Target package must belong to the repository using this action.


.. jinja:: hk-package-clean-except

    {{ inputs_table }}

    Examples
    ++++++++

    {% for filename, title in examples %}
    .. dropdown:: {{ title }}
       :animate: fade-in

        .. literalinclude:: examples/{{ filename }}
           :language: yaml

    {% endfor %}

