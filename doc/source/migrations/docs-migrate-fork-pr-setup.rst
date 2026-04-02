.. _hk-migrate-fork-pr-setup:

Migrating pull requests originating from forks
==============================================

The ``ansys/actions/hk-migrate-fork-pr`` action migrates pull requests opened
from forks into branches inside the main repository. This is sometimes necessary because
GitHub does not expose repository secrets to workflows triggered by fork PRs, so
CI pipelines that require secrets cannot run successfully.

The action creates a ``migration/pr-<N>`` branch in the main repository that is a
mirror of the fork's branch, then opens a new pull request targeting ``main``.
Subsequent syncs keep the migration branch up to date with the contributor's fork.

.. important::

   **Required token scopes and workflow permissions**

   The ``github-token`` input must be a token with the following permissions:

   - ``contents: write`` — push migration branches
   - ``pull-requests: write`` — create PRs, manage comments and reactions
   
   Additionally, the provided ``github-token`` must have ``read:org`` scope
   to check team membership for authorization.

   The workflow job must declare:

   .. code:: yaml

       permissions:
         contents: write
         pull-requests: write

Setup
-----

The action listens for ``issue_comment`` events on pull requests and
triggers when a team member posts ``@pyansys-ci-bot migrate`` (first migration)
or ``@pyansys-ci-bot sync`` (subsequent sync).

Typical setup might involve creating or updating a ``.github/workflows/migrate-fork-pr.yml``
workflow with the following content:

.. code:: yaml

    name: Migrate fork PR

    on:
      issue_comment:
        types: [created]

    jobs:
      hk-migrate-fork-pr:
        name: "Migrate fork PR to main repository"
        runs-on: ubuntu-latest
        if: |
          github.event_name == 'issue_comment' &&
          github.event.issue.pull_request != null &&
          (contains(github.event.comment.body, '@pyansys-ci-bot migrate') ||
           contains(github.event.comment.body, '@pyansys-ci-bot sync'))
        permissions:
          contents: write
          pull-requests: write
        steps:
          - name: "Migrate fork PR"
            uses: ansys/actions/hk-migrate-fork-pr@{{ version }}
            with:
              pr-number: ${{ github.event.issue.number }}
              comment-id: ${{ github.event.comment.id }}
              user-triggering: ${{ github.event.comment.user.login }}
              github-token: ${{ secrets.PYANSYS_CI_BOT_TOKEN }}
              bot-username: ${{ secrets.PYANSYS_CI_BOT_USERNAME }}
              bot-email: ${{ secrets.PYANSYS_CI_BOT_EMAIL }}
              team-slug: 'pyansys-maintainers'

.. note::

   Replace ``team-slug`` with the slug of the GitHub team whose members are
   authorised to trigger migrations (for example, ``pymapdl-maintainers``).


How the action works
---------------------

The following describes the end-to-end flow from both the contributor's and the
maintainer's perspective.

**First migration**

1. An external contributor opens a pull request from their fork.
2. A maintainer comments ``@pyansys-ci-bot migrate`` on the fork PR.
3. The action verifies that the commenter is a member of the configured team.
4. A ``migration/pr-<N>`` branch is created in the main repository as an exact
   mirror of the fork branch.
5. A new pull request targeting ``main`` is opened automatically.
6. A success comment is posted on the fork PR explaining the workflow to the
   contributor (see :ref:`contributor-workflow` below).

**Subsequent syncs**

1. The contributor pushes new commits to their fork branch as normal.
2. When CI needs to run against the latest changes, a maintainer comments
   ``@pyansys-ci-bot sync`` on the fork PR.
3. The action mirrors the fork branch onto the migration branch again, and CI
   triggers on the migration PR.

At no point does the contributor need write access to the main repository.

.. _contributor-workflow:

Contributor workflow
''''''''''''''''''''

After the first migration, contributors should:

- Continue pushing commits to their **own fork branch** exactly as they would
  for any pull request.
- When they want their latest changes reflected in the migration PR, leave a
  comment on the fork PR tagging a member of the maintainer team and asking for
  a sync.
- **Not** push directly to the ``migration/pr-<N>`` branch — they do not have
  access to it, and a subsequent sync would overwrite any such changes anyway.


.. note::

   If a maintainer merged ``main`` into the migration branch directly, and the fork
   branch has not received that same merge, a sync would silently discard those
   commits. The action detects this situation and blocks the sync with an
   explanatory comment on the fork PR.

   When this happens, the contributor must first merge ``main`` into their fork
   branch. Once the fork branch is up to date, the maintainer can trigger the sync again.
