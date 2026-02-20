# Fork PR Migration Action

This action migrates pull requests from forks to branches in the main repository, enabling workflows that require repository secrets to run.

## Features

- **Team-based authorization**: Verifies that the user triggering the migration is a member of a specified GitHub team
- **Conflict resolution**: Supports multiple strategies (auto, theirs, ours) for handling merge conflicts
- **Automated PR creation**: Automatically creates a new PR in the main repository with proper references
- **Rich notifications**: Provides feedback through reactions and comments on the original PR

## Required Secrets

To use this action, you need to configure the following secrets in your repository:

- `PYANSYS_CI_BOT_TOKEN`: GitHub token with `contents: write` and `pull-requests: write` permissions
- `PYANSYS_CI_BOT_TEAMS_READ_TOKEN`: GitHub token with `read:org` permissions to check team membership
- `PYANSYS_CI_BOT_USERNAME`: Username of the bot account
- `PYANSYS_CI_BOT_EMAIL`: Email address of the bot account

## Usage

### Trigger the migration

Users with appropriate team membership can trigger the migration by commenting on a forked PR:

- `@pyansys-ci-bot migrate` - Migrate the PR (fail if conflicts)
- `@pyansys-ci-bot migrate theirs` - Migrate and resolve conflicts using fork changes
- `@pyansys-ci-bot migrate ours` - Migrate and resolve conflicts using main branch changes
- `@pyansys-ci-bot sync` - Alternative syntax (same behavior as migrate)

### Example workflow

Create a workflow file (e.g., `.github/workflows/fork-pr-handler.yml`):

```yaml
name: "Fork PR Migration Handler"

on:
  issue_comment:
    types: [created]

permissions: {}

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  migrate:
    name: "Migrate fork PR"
    if: |
      github.event.issue.pull_request != null &&
      (contains(github.event.comment.body, '@pyansys-ci-bot migrate') ||
       contains(github.event.comment.body, '@pyansys-ci-bot sync'))
    runs-on: ubuntu-latest
    permissions:
      contents: write
      pull-requests: write
    steps:
      - name: "Migrate fork PR"
        uses: ansys/actions/hk-migrate-fork-pr@v8
        with:
          pr-number: ${{ github.event.issue.number }}
          comment-id: ${{ github.event.comment.id }}
          user-triggering: ${{ github.event.comment.user.login }}
          github-token: ${{ secrets.PYANSYS_CI_BOT_TOKEN }}
          team-read-token: ${{ secrets.PYANSYS_CI_BOT_TEAMS_READ_TOKEN }}
          bot-username: ${{ secrets.PYANSYS_CI_BOT_USERNAME }}
          bot-email: ${{ secrets.PYANSYS_CI_BOT_EMAIL }}
          team-slug: 'your-team-slug'
```

## Inputs

See [action.yml](action.yml) for detailed input documentation.

## How it works

1. Validates that the user triggering the migration is a member of the specified team
2. Retrieves details about the fork PR
3. Creates a new branch in the main repository (`migration/pr-<number>`)
4. Fetches the fork branch and merges it with main
5. Handles merge conflicts according to the specified strategy
6. Pushes the migration branch to the main repository
7. Creates a new PR linking to the original fork PR
8. Assigns the PR to both the triggering user and the original author
9. Adds reactions and comments to indicate success or failure

## Conflict Resolution Modes

- **auto** (default): Migration fails if conflicts are detected
- **theirs**: Automatically resolves conflicts by accepting changes from the fork branch
- **ours**: Automatically resolves conflicts by accepting changes from the main branch

## Security Considerations

- Requires separate tokens for general operations and team membership checks
- Only team members can trigger migrations
- Uses workflow permissions to enforce least privilege
- Includes security annotations for static analysis tools (e.g., zizmor)
