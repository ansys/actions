# Tag Repository Version

This action will:

- update the vX and vX.Y tags to point to the latest releases of the repository.
- create a `release/vX.Y.Z` branch and push a copy to the repository

## ! Important

This action is intended to be used in a workflow triggered by a release event.

## Example usage

Via workflow file:

<pre lang="yaml">
on:
  release:
    types: [published]

jobs:
  update_latest_version_branch_tag:
    runs-on: ubuntu-latest
    steps:
      - name: Update Latest vX and vX.Y Tag
        uses: ansys-internal/actions/tag-repository-version@&#x6;5 <!-- x-release-please-major -->
        with:
          gh-token: ${{ secrets.GITHUB_TOKEN }}
</pre>

Or via step:

<pre lang="yaml">
steps:
  - name: Tag Repository with Release Version
    if: github.event_name == 'release'
    uses: ansys-internal/actions/tag-repository-version@&#x6;5 <!-- x-release-please-major -->
    with:
      gh-token: ${{ secrets.GITHUB_TOKEN }}
</pre>