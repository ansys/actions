Documentation actions
=====================

Documentation actions build and deploy the documentation of
a PyAnsys project.

To use these actions, a project must use `Sphinx <https://www.sphinx-doc.org/en/master/>`_
as documentation parser.


Doc build action
----------------
This action builds the documentation of a PyAnsys project using the
`sphinx-build <https://www.sphinx-doc.org/en/master/man/sphinx-build.html>`_
command. 

It uses ``HTML``, ``PDF``, and ``JSON`` builders to generate the following
artifacts:

* ``documentation-html``: Web-based documentation to display in the ``gh-pages`` branch.
* ``documentation-pdf``: File-based documentation to use in offline tasks.
* ``documetation-json``: Documentation that is to be consumed by the Ansys developer's portal.

.. jinja:: doc-build

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
This action deploys ``HTML`` documentation into the ``gh-pages`` branch. It is
expected to be used after the :ref:`Doc build action` because it looks for an
artifact named ``documentation-html``.

.. jinja:: doc-deploy-dev

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
This action deploys ``HTML`` documentation into the ``release/`` directory of
the ``gh-pages`` branch. It is expected to be used after the :ref:`Doc build
action` because it looks for an artifact named ``documentation-html``.

The logic behind this action is smart enough to identify the major and minor
versions of your stable documentation and generate a new folder named
``<MAJOR>.<MINOR>``. If this directory already exists, its content is overridden.

The ``release/`` directory is expected to contain a JSON file for version
mapping, as specified in `Version switcher dropdowns
<https://pydata-sphinx-theme.readthedocs.io/en/stable/user_guide/version-dropdown.html#version-switcher-dropdowns>`_
in the `PyData Theme
<https://pydata-sphinx-theme.readthedocs.io/en/stable/index.html>`_ for Sphinx output.

In addition, the ``conf.py`` file is expected to contain the following keys and
values inside the ``html_theme_options`` element:

.. code-block:: python

    import ansys_sphinx_theme


    html_theme_options = {
        "switcher": {
            "json_url": f"https://{cname}/release/versions.json",
            "version_match": ansys_sphinx_theme.get_version_match(__version__),
        },
        ...
    }

All previous logic supports multi-version documentation history in
a PyAnsys project.

.. jinja:: doc-deploy-stable

    {{ inputs_table }}

    Examples
    ++++++++

    {% for filename, title in examples %}
    .. dropdown:: {{ title }}
       :animate: fade-in

        .. literalinclude:: examples/{{ filename }}
           :language: yaml

    {% endfor %}


Doc deploy action to other repositories
---------------------------------------
This action deploys ``HTML`` documentation into the ``gh-pages`` branch of a different
repository. It is expected to be used after the :ref:`Doc build action` because it looks
for an artifact named ``documentation-html``.

Following the needs of the different PyAnsys libraries, it may occur that the repository
for which the documentation is being build is not public yet. For those cases, the
multi-version mechanism (which the previous actions assume) is not allowed.

The way PyAnsys libraries handle documentation deployment while being private/internal is
by releasing its documentation to dedicated repositories: one for the dev documentation, and
a different one for the stable (or internally released) documentation. This action intends
to allow users to specify which repository they intend to release their docs to.

The PyAnsys CI bot should be allowed to access the targeted documentation repository in order
to be able to publish your documentation. If for any reason a different bot is used, please look
at the optional arguments for this action.

.. jinja:: doc-deploy-to-repo

    {{ inputs_table }}

    Examples
    ++++++++

    {% for filename, title in examples %}
    .. dropdown:: {{ title }}
       :animate: fade-in

        .. literalinclude:: examples/{{ filename }}
           :language: yaml

    {% endfor %}


