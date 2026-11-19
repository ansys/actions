Housekeeping actions
====================
Housekeeping actions provide for general repository operations such as package cleanup.


Package cleanup of untagged versions
------------------------------------

.. jinja:: hk-package-clean-untagged
    :file: _templates/action.rst.jinja

Package cleanup excluding certain versions
------------------------------------------

.. jinja:: hk-package-clean-except
    :file: _templates/action.rst.jinja

Auto-merge pull requests
------------------------

.. jinja:: hk-automerge-prs
    :file: _templates/action.rst.jinja

Label pull requests from trailers
---------------------------------

.. jinja:: hk-label-from-trailers
    :file: _templates/action.rst.jinja

List trailer names in ``direct-trailers`` when the label should be derived
from the trailer name, and in ``value-trailers`` when its comma-separated
values should be used as labels. Both kinds of generated labels are lowercase.
Semicolons are not accepted as separators, and the corresponding repository
labels must already exist. Trailers must be in the first level-2 section
(starting at the first ``##`` heading) of the PR description; otherwise the
action emits a warning and does not apply labels. For example:

.. code-block:: text

    ## Description

    Some description of the changes made in this pull request.

    Product-version: 25R1, 25R2
    Breaking-changes: Remove compatibility with older servers
    Deprecation: The legacy endpoint will be removed

Together, these trailers add two version labels, the ``breaking-changes`` label, and the
``deprecation`` label:

.. code-block:: yaml

    permissions:
      pull-requests: write

    steps:
      - uses: ansys/actions/hk-label-from-trailers@v11
        with:
          direct-trailers: Breaking-changes, Deprecation
          value-trailers: Product-version

The version labels added by this example are ``25r1`` and ``25r2``.

Migrate fork pull requests
---------------------------

.. jinja:: hk-migrate-fork-pr
    :file: _templates/action.rst.jinja

Tag repository version
----------------------

.. jinja:: hk-tag-repository-version
    :file: _templates/action.rst.jinja

Auto release
------------

.. jinja:: hk-autorelease
    :file: _templates/action.rst.jinja
