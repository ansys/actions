# IMPORTANT: migration from `ignored-safety.txt` to `.safety-ignore.yml`

We have migrated from using `ignored-safety.txt` to `.safety-ignore.yml` for managing ignored
vulnerabilities. Especially for `ansys/actions` maintainers, make sure that whenever a new
vulnerability is added to `.safety-ignore.yml`, it is also added to `ignored-safety.txt` until
the migration is complete. This ensures that the CI checks continue to function correctly
during the transition period.

> [!IMPORTANT]
> The `ignored-safety.txt` file is still required for the consumers of this action to work properly. Old action
> versions will continue to use `ignored-safety.txt` until repository maintainers upgrade to the latest
> version of the action that supports `.safety-ignore.yml`.
