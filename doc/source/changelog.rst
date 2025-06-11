.. _ref_release_notes:

Release notes
#############

This document contains the release notes for the Ansys Actions project.

.. vale off

.. towncrier release notes start

`10.0.10 <https://github.com/ansys/actions/releases/tag/v10.0.10>`_ - June 11, 2025
===================================================================================

.. tab-set::


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Bump softprops/action-gh-release from 2.2.2 to 2.3.2 in /release-github in the release-related-actions group across 1 directory
          - `#903 <https://github.com/ansys/actions/pull/903>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Wrong variable name for sphinx options
          - `#900 <https://github.com/ansys/actions/pull/900>`_

        * - Variable resolution
          - `#901 <https://github.com/ansys/actions/pull/901>`_


`10.0.9 <https://github.com/ansys/actions/releases/tag/v10.0.9>`_ - June 10, 2025
=================================================================================

.. tab-set::


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update the description of the option named package-org.
          - `#893 <https://github.com/ansys/actions/pull/893>`_

        * - Document installation by uv
          - `#896 <https://github.com/ansys/actions/pull/896>`_


`10.0.8 <https://github.com/ansys/actions/releases/tag/v10.0.8>`_ - June 06, 2025
=================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Release-github artifacts attestation
          - `#890 <https://github.com/ansys/actions/pull/890>`_


`10.0.7 <https://github.com/ansys/actions/releases/tag/v10.0.7>`_ - June 06, 2025
=================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Doc build on windows input issues
          - `#888 <https://github.com/ansys/actions/pull/888>`_


`10.0.6 <https://github.com/ansys/actions/releases/tag/v10.0.6>`_ - June 05, 2025
=================================================================================

.. tab-set::


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Use bash shell for windows
          - `#879 <https://github.com/ansys/actions/pull/879>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Raise warning if not using trusted publishers
          - `#883 <https://github.com/ansys/actions/pull/883>`_

        * - Missing skip-existing command handling
          - `#884 <https://github.com/ansys/actions/pull/884>`_


`10.0.5 <https://github.com/ansys/actions/releases/tag/v10.0.5>`_ - June 05, 2025
=================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Missing environment variable on pypi releasing
          - `#880 <https://github.com/ansys/actions/pull/880>`_


`10.0.4 <https://github.com/ansys/actions/releases/tag/v10.0.4>`_ - June 04, 2025
=================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Doc-deploy-changelog
          - `#876 <https://github.com/ansys/actions/pull/876>`_


`10.0.3 <https://github.com/ansys/actions/releases/tag/v10.0.3>`_ - June 03, 2025
=================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Smoke test for poetry projects in editable mode
          - `#875 <https://github.com/ansys/actions/pull/875>`_


`10.0.2 <https://github.com/ansys/actions/releases/tag/v10.0.2>`_ - June 03, 2025
=================================================================================

.. tab-set::


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Remove the usage of uv for doc-deploy-changelog
          - `#874 <https://github.com/ansys/actions/pull/874>`_


`10.0.1 <https://github.com/ansys/actions/releases/tag/v10.0.1>`_ - June 03, 2025
=================================================================================

.. tab-set::


  .. tab-item:: Added

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - check actions security action
          - `#725 <https://github.com/ansys/actions/pull/725>`_

        * - uv as default package manager
          - `#754 <https://github.com/ansys/actions/pull/754>`_

        * - check environment approval
          - `#776 <https://github.com/ansys/actions/pull/776>`_

        * - add compatibility with dependency groups
          - `#794 <https://github.com/ansys/actions/pull/794>`_

        * - pr documentation deployment and cleanup
          - `#799 <https://github.com/ansys/actions/pull/799>`_

        * - allow to specify working-directory
          - `#820 <https://github.com/ansys/actions/pull/820>`_

        * - option for maximum number of pr doc deployment
          - `#823 <https://github.com/ansys/actions/pull/823>`_

        * - ensure matching and metadata version
          - `#833 <https://github.com/ansys/actions/pull/833>`_

        * - add SBOM to wheelhouse action
          - `#834 <https://github.com/ansys/actions/pull/834>`_

        * - change branch naming in changelog action
          - `#837 <https://github.com/ansys/actions/pull/837>`_

        * - Support specification of ``bandit`` configuration file in check-vulnerabilities action
          - `#838 <https://github.com/ansys/actions/pull/838>`_

        * - capitalize fragments
          - `#852 <https://github.com/ansys/actions/pull/852>`_

        * - Prepend link to migration guide in github release notes
          - `#860 <https://github.com/ansys/actions/pull/860>`_

        * - Implementing basic smoke test for import
          - `#866 <https://github.com/ansys/actions/pull/866>`_


  .. tab-item:: Dependencies

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - bump actions/download-artifact from 4.1.9 to 4.2.1 in the github-actions group
          - `#770 <https://github.com/ansys/actions/pull/770>`_

        * - update action-gh-release
          - `#777 <https://github.com/ansys/actions/pull/777>`_

        * - bump softprops/action-gh-release from 2.2.1 to 2.2.2 in the release-related-actions group
          - `#786 <https://github.com/ansys/actions/pull/786>`_

        * - bump actions/download-artifact from 4.2.1 to 4.3.0 in the github-actions group
          - `#795 <https://github.com/ansys/actions/pull/795>`_

        * - update pygithub requirement from <2,>=1.59 to >=1.59,<3 in /check-vulnerabilities
          - `#842 <https://github.com/ansys/actions/pull/842>`_

        * - bump awalsh128/cache-apt-pkgs-action from 1.4.3 to 1.5.0 in /_doc-build-linux in the doc-related-actions group across 1 directory
          - `#845 <https://github.com/ansys/actions/pull/845>`_

        * - Bump the build-related-actions group across 1 directory with 2 updates
          - `#846 <https://github.com/ansys/actions/pull/846>`_

        * - bump softprops/action-gh-release from 2.2.1 to 2.2.2 in /release-github in the release-related-actions group across 1 directory
          - `#847 <https://github.com/ansys/actions/pull/847>`_

        * - bump dependabot/fetch-metadata from 2.3.0 to 2.4.0 in /hk-automerge-prs in the must-be-assigned-actions group across 1 directory
          - `#848 <https://github.com/ansys/actions/pull/848>`_

        * - bump the github-actions group across 11 directories with 4 updates
          - `#849 <https://github.com/ansys/actions/pull/849>`_

        * - Downgrade awalsh128/cache-apt-pkgs-action due to errors
          - `#856 <https://github.com/ansys/actions/pull/856>`_

        * - Bump the github-actions group across 1 directory with 2 updates
          - `#863 <https://github.com/ansys/actions/pull/863>`_

        * - Bump the build-related-actions group across 2 directories with 1 update
          - `#865 <https://github.com/ansys/actions/pull/865>`_


  .. tab-item:: Documentation

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Update documentation for v10 release
          - `#828 <https://github.com/ansys/actions/pull/828>`_


  .. tab-item:: Fixed

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - environment variable is missing after ``zizmor`` refactor
          - `#796 <https://github.com/ansys/actions/pull/796>`_

        * - ci_cd_release action
          - `#800 <https://github.com/ansys/actions/pull/800>`_

        * - install from poetry.lock if present
          - `#805 <https://github.com/ansys/actions/pull/805>`_

        * - remove marshmallow dependency limit
          - `#806 <https://github.com/ansys/actions/pull/806>`_

        * - allow to specify working directory
          - `#807 <https://github.com/ansys/actions/pull/807>`_

        * - avoid using pip cache with uv
          - `#811 <https://github.com/ansys/actions/pull/811>`_

        * - properly use poetry wheelhouse
          - `#817 <https://github.com/ansys/actions/pull/817>`_

        * - remove JSON builds
          - `#818 <https://github.com/ansys/actions/pull/818>`_

        * - build wheelhouse with poetry
          - `#826 <https://github.com/ansys/actions/pull/826>`_

        * - documentation
          - `#827 <https://github.com/ansys/actions/pull/827>`_

        * - input parameter generate-release-notes in release-github
          - `#832 <https://github.com/ansys/actions/pull/832>`_

        * - update to latest version
          - `#839 <https://github.com/ansys/actions/pull/839>`_

        * - discovery of artifacts in release-github
          - `#840 <https://github.com/ansys/actions/pull/840>`_

        * - default value for prune-uv-cache
          - `#850 <https://github.com/ansys/actions/pull/850>`_

        * - Housekeeping package clean actions
          - `#855 <https://github.com/ansys/actions/pull/855>`_

        * - Release-github python setup and sbom pattern
          - `#871 <https://github.com/ansys/actions/pull/871>`_

        * - Create a virtual environment in the changelog deployment action
          - `#872 <https://github.com/ansys/actions/pull/872>`_

        * - Install packages at system level
          - `#873 <https://github.com/ansys/actions/pull/873>`_


  .. tab-item:: Maintenance

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - update CHANGELOG for v9.0.0
          - `#768 <https://github.com/ansys/actions/pull/768>`_

        * - update CHANGELOG for v9.0.1
          - `#772 <https://github.com/ansys/actions/pull/772>`_

        * - rewrite dependabot checks
          - `#774 <https://github.com/ansys/actions/pull/774>`_

        * - update CHANGELOG for v9.0.2
          - `#775 <https://github.com/ansys/actions/pull/775>`_

        * - update CHANGELOG for v9.0.3
          - `#781 <https://github.com/ansys/actions/pull/781>`_

        * - update CHANGELOG for v9.0.6
          - `#785 <https://github.com/ansys/actions/pull/785>`_

        * - update CHANGELOG for v9.0.7
          - `#792 <https://github.com/ansys/actions/pull/792>`_

        * - update CHANGELOG for v9.0.8
          - `#801 <https://github.com/ansys/actions/pull/801>`_

        * - use ansys/actions/doc-deploy-pr
          - `#802 <https://github.com/ansys/actions/pull/802>`_

        * - update uv settings
          - `#825 <https://github.com/ansys/actions/pull/825>`_

        * - remove deprecated line
          - `#830 <https://github.com/ansys/actions/pull/830>`_

        * - update dependabot inputs to match groups
          - `#841 <https://github.com/ansys/actions/pull/841>`_

        * - Update changelog for v9.0.12
          - `#854 <https://github.com/ansys/actions/pull/854>`_

        * - Improve smoke tests handling
          - `#861 <https://github.com/ansys/actions/pull/861>`_

        * - Add sbom artifacts to github release
          - `#862 <https://github.com/ansys/actions/pull/862>`_

        * - Update changelog for v9.0.13
          - `#869 <https://github.com/ansys/actions/pull/869>`_


  .. tab-item:: Miscellaneous

    .. list-table::
        :header-rows: 0
        :widths: auto

        * - Allow to mix dependency groups and optional targets
          - `#836 <https://github.com/ansys/actions/pull/836>`_


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
