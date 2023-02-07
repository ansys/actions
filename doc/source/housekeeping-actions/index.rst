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
* The package to be dealt with should belong to the repository where this action is
  being used.

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


Package cleanup except for certain versions
-------------------------------------------
This action cleans up **all** the package versions published in
`ghcr.io <https://ghcr.io/>`_ **except for a list of tags**. This is useful for scheduled
package uploads that keep updating a tag while leaving other tags behind.

Requirements for running this action:

* A token with **write package permissions** is needed.
* A list of tags to be kept, such as ``latest, latest-unstable``.
* The package to be dealt with should belong to the repository where this action is
  being used.

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

