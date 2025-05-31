.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the Ansys Actions project.

.. vale off

.. towncrier release notes start

`9.0.13 <https://github.com/ansys/actions/releases/tag/v9.0.13>`_ - May 30, 2025
================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Advanced search path
          - `#868 <https://github.com/ansys/actions/pull/868>`_


`9.0.12 <https://github.com/ansys/actions/releases/tag/v9.0.12>`_ - May 26, 2025
================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Check licenses logic alignment
          - `#853 <https://github.com/ansys/actions/pull/853>`_


`9.0.8 <https://github.com/ansys/actions/releases/tag/v9.0.8>`_ - May 06, 2025
==============================================================================

.. tab-set::


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - remove deprecations and v8 refs
          - `#798 <https://github.com/ansys/actions/pull/798>`_


`9.0.7 <https://github.com/ansys/actions/releases/tag/v9.0.7>`_ - April 29, 2025
================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - pin quarto version
          - `#791 <https://github.com/ansys/actions/pull/791>`_


`9.0.6 <https://github.com/ansys/actions/releases/tag/v9.0.6>`_ - April 21, 2025
================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - skip installation on doc-deploy-changelog
          - `#782 <https://github.com/ansys/actions/pull/782>`_

        * - add package key in towncrier.toml
          - `#783 <https://github.com/ansys/actions/pull/783>`_

        * - Add newline between environment variables in Python
          - `#784 <https://github.com/ansys/actions/pull/784>`_


`9.0.3 <https://github.com/ansys/actions/releases/tag/v9.0.3>`_ - April 18, 2025
================================================================================

.. tab-set::


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - add upper bound on marshmallow
          - `#780 <https://github.com/ansys/actions/pull/780>`_


`9.0.2 <https://github.com/ansys/actions/releases/tag/v9.0.2>`_ - April 09, 2025
================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - build-wheelhouse: remove new lines inside run block
          - `#761 <https://github.com/ansys/actions/pull/761>`_


`9.0.1 <https://github.com/ansys/actions/releases/tag/v9.0.1>`_ - April 09, 2025
================================================================================

.. tab-set::


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - fix link
          - `#769 <https://github.com/ansys/actions/pull/769>`_


`9.0.0 <https://github.com/ansys/actions/releases/tag/v9.0.0>`_ - April 08, 2025
================================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - bump sphinx from 8.2.1 to 8.2.3 in /requirements
          - `#710 <https://github.com/ansys/actions/pull/710>`_

        * - bump ansys-sphinx-theme from 1.3.2 to 1.3.3 in /requirements
          - `#729 <https://github.com/ansys/actions/pull/729>`_

        * - bump the github-actions group with 2 updates
          - `#746 <https://github.com/ansys/actions/pull/746>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - setup changelog
          - `#699 <https://github.com/ansys/actions/pull/699>`_

        * - add SECURITY.md
          - `#709 <https://github.com/ansys/actions/pull/709>`_

        * - add CONTRIBUTING.md
          - `#712 <https://github.com/ansys/actions/pull/712>`_

        * - change migration guide version to v8.2
          - `#713 <https://github.com/ansys/actions/pull/713>`_

        * - extend v8.2 new features notes
          - `#718 <https://github.com/ansys/actions/pull/718>`_

        * - log deprecation only for trusted publishers
          - `#719 <https://github.com/ansys/actions/pull/719>`_

        * - fix vale warning
          - `#737 <https://github.com/ansys/actions/pull/737>`_

        * - do not check link on www.x.org/*
          - `#755 <https://github.com/ansys/actions/pull/755>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - use ansys/pip-licenses to handle PEP 639
          - `#698 <https://github.com/ansys/actions/pull/698>`_

        * - syntax
          - `#714 <https://github.com/ansys/actions/pull/714>`_

        * - avoids installing project and provides support for non-python projects
          - `#715 <https://github.com/ansys/actions/pull/715>`_

        * - rolling release job
          - `#716 <https://github.com/ansys/actions/pull/716>`_

        * - major variable
          - `#717 <https://github.com/ansys/actions/pull/717>`_

        * - default should be false for "generate release notes" entry
          - `#745 <https://github.com/ansys/actions/pull/745>`_

        * - drop build and wheel packages
          - `#756 <https://github.com/ansys/actions/pull/756>`_

        * - optional build and wheel installation
          - `#762 <https://github.com/ansys/actions/pull/762>`_

        * - use trusted publishers from PyPA action
          - `#763 <https://github.com/ansys/actions/pull/763>`_

        * - github-ref
          - `#764 <https://github.com/ansys/actions/pull/764>`_

        * - tag check
          - `#766 <https://github.com/ansys/actions/pull/766>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - nightly deployment does not have the CNAME
          - `#711 <https://github.com/ansys/actions/pull/711>`_

        * - update CHANGELOG for v8.2.11
          - `#721 <https://github.com/ansys/actions/pull/721>`_

        * - update CHANGELOG for v8.2.13
          - `#724 <https://github.com/ansys/actions/pull/724>`_

        * - update CHANGELOG for v8.2.16
          - `#728 <https://github.com/ansys/actions/pull/728>`_

        * - update CHANGELOG for v8.2.26
          - `#733 <https://github.com/ansys/actions/pull/733>`_

        * - update CHANGELOG for v8.2.27
          - `#741 <https://github.com/ansys/actions/pull/741>`_

        * - update CHANGELOG for v8.2.28
          - `#743 <https://github.com/ansys/actions/pull/743>`_

        * - update CHANGELOG for v8.2.30
          - `#749 <https://github.com/ansys/actions/pull/749>`_

        * - changelog action should depend on rolling release
          - `#750 <https://github.com/ansys/actions/pull/750>`_

        * - refactor logic for PRs opened by dependabot
          - `#751 <https://github.com/ansys/actions/pull/751>`_

        * - add dependabot cooldown for pip
          - `#752 <https://github.com/ansys/actions/pull/752>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - warn about release pypi deprecation and encourage to use trusted publisher
          - `#707 <https://github.com/ansys/actions/pull/707>`_

        * - use SHA version for pypa/gh-action-pypi-publish
          - `#734 <https://github.com/ansys/actions/pull/734>`_

        * - use full length commit SHA instead of tags for external github actions
          - `#739 <https://github.com/ansys/actions/pull/739>`_

        * - remove trusted publisher
          - `#758 <https://github.com/ansys/actions/pull/758>`_


`8.2.30 <https://github.com/ansys/actions/releases/tag/v8.2.30>`_ - March 25, 2025
==================================================================================

.. tab-set::


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - clarify comment statement on release-github action
          - `#748 <https://github.com/ansys/actions/pull/748>`_


`8.2.28 <https://github.com/ansys/actions/releases/tag/v8.2.28>`_ - March 21, 2025
==================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - sanity check on inputs for release-github action
          - `#742 <https://github.com/ansys/actions/pull/742>`_


`8.2.27 <https://github.com/ansys/actions/releases/tag/v8.2.27>`_ - March 20, 2025
==================================================================================

.. tab-set::


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - add documentation on automerge action
          - `#740 <https://github.com/ansys/actions/pull/740>`_


`8.2.26 <https://github.com/ansys/actions/releases/tag/v8.2.26>`_ - March 14, 2025
==================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - release-github body
          - `#732 <https://github.com/ansys/actions/pull/732>`_


`8.2.16 <https://github.com/ansys/actions/releases/tag/v8.2.16>`_ - March 11, 2025
==================================================================================

.. tab-set::


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - fix github variable
          - `#727 <https://github.com/ansys/actions/pull/727>`_


`8.2.13 <https://github.com/ansys/actions/releases/tag/v8.2.13>`_ - March 06, 2025
==================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - install for Python libraries
          - `#723 <https://github.com/ansys/actions/pull/723>`_


`8.2.11 <https://github.com/ansys/actions/releases/tag/v8.2.11>`_ - March 05, 2025
==================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - tags
          - `#720 <https://github.com/ansys/actions/pull/720>`_


`8.2.10 <https://github.com/ansys/actions/releases/tag/v8.2.10>`_ - March 05, 2025
==================================================================================

.. tab-set::


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - extend v8.2 new features notes
          - `#718 <https://github.com/ansys/actions/pull/718>`_

        * - log deprecation only for trusted publishers
          - `#719 <https://github.com/ansys/actions/pull/719>`_


`8.2.5 <https://github.com/ansys/actions/releases/tag/v8.2.5>`_ - March 04, 2025
================================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - bump sphinx from 8.2.1 to 8.2.3 in /requirements
          - `#710 <https://github.com/ansys/actions/pull/710>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - setup changelog
          - `#699 <https://github.com/ansys/actions/pull/699>`_

        * - add SECURITY.md
          - `#709 <https://github.com/ansys/actions/pull/709>`_

        * - add CONTRIBUTING.md
          - `#712 <https://github.com/ansys/actions/pull/712>`_

        * - change migration guide version to v8.2
          - `#713 <https://github.com/ansys/actions/pull/713>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - syntax
          - `#714 <https://github.com/ansys/actions/pull/714>`_

        * - avoids installing project and provides support for non-python projects
          - `#715 <https://github.com/ansys/actions/pull/715>`_

        * - rolling release job
          - `#716 <https://github.com/ansys/actions/pull/716>`_

        * - major variable
          - `#717 <https://github.com/ansys/actions/pull/717>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - nightly deployment does not have the CNAME
          - `#711 <https://github.com/ansys/actions/pull/711>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - warn about release pypi deprecation and encourage to use trusted publisher
          - `#707 <https://github.com/ansys/actions/pull/707>`_
