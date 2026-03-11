# Example Custom Safety Policy File

This is an example of a custom `.safety-ignore.yaml` file that can be placed in your repository
and referenced using the `safety-policy-file` input parameter.

## File Location
Place this file anywhere in your repository, for example:
- `.safety-ignore.yaml` (root of repository)
- `.github/.safety-ignore.yaml`
- `config/safety-ignore.yaml`

## Example Content

```yaml
# Custom Safety ignore file for project-specific vulnerabilities
# Documentation: https://docs.pyup.io/docs/safety-20-policy-file

security:
  ignore-vulnerabilities:
    # Example: Ignore a specific vulnerability with detailed reason
    70612:
      reason: "False positive - does not affect our usage"
      expires: "2026-12-31"
    
    # Example: Ignore with no expiration
    71064:
      reason: "Dependency constraint prevents upgrade"
      expires: null
    
    # Example: Temporarily ignore during investigation
    72450:
      reason: "Under investigation by security team"
      expires: "2026-06-30"
    
    # You can also include the default ones from the action if needed
    # Default vulnerabilities from ansys/actions:
    52495:
      reason: "Accepted vulnerability"
      expires: null
    62044:
      reason: "Accepted vulnerability"
      expires: null
    67599:
      reason: "Accepted vulnerability"
      expires: null
    72236:
      reason: "Accepted vulnerability"
      expires: null
    76752:
      reason: "Accepted vulnerability"
      expires: null
    83150:
      reason: "Accepted vulnerability"
      expires: null
```

## Usage in Workflow

```yaml
- name: "Check vulnerabilities"
  uses: ansys/actions/check-vulnerabilities@main
  with:
    token: ${{ secrets.GITHUB_TOKEN }}
    python-package-name: "my-package"
    safety-policy-file: ".safety-ignore.yaml"  # or your custom path
```

## How It Works

1. **Without `safety-policy-file`**: Uses the default `.safety-ignore.yaml` from the action
2. **With `safety-policy-file`**: Uses **only** your custom file (replaces the default)

This is an **either/or** choice - if you provide a custom file, it completely replaces the default one.

## Important Note

If you provide a custom safety policy file, it will be used **instead of** the default one.
This means you need to include **all** vulnerabilities you want to ignore in your custom file,
including the ones from the default action if you want to keep them.

## Benefits

- ✅ Full control over which vulnerabilities to ignore
- ✅ Document why each vulnerability is ignored
- ✅ Set expiration dates for temporary ignores
- ✅ Project-specific configuration
- ✅ Easy to maintain and version control
