# Repository Review: ansys/actions

Comprehensive audit of the `ansys/actions` repository covering **security**, **technology modernization**, **code quality**, and **best practices**.

---

## Executive Summary

The repository is overall **well-maintained** with strong security fundamentals — pinned commit SHAs, zizmor auditing, Dependabot, and a supply-chain-attack mitigation strategy for Dependabot PRs. However, there are several concrete improvements across security hardening, technology upgrades, and code quality.

---

## 🔒 Security Improvements

### 1. MD5 Hashing in `check_vulnerabilities.py` — Use SHA-256

**File**: [check_vulnerabilities.py](file:///d:/PyAnsys/Repos/actions/check-vulnerabilities/check_vulnerabilities.py#L64)

```python
# Current (line 64)
dhash = hashlib.md5()
```

MD5 is cryptographically broken and flagged by most security scanners. Even for non-cryptographic fingerprinting, SHA-256 is the modern standard and avoids audit noise.

```diff
- dhash = hashlib.md5()
+ dhash = hashlib.sha256()
```

### 2. Bare `except:` Clauses in `check_vulnerabilities.py`

**File**: [check_vulnerabilities.py](file:///d:/PyAnsys/Repos/actions/check-vulnerabilities/check_vulnerabilities.py#L349-L358)

```python
# Lines 349 and 358
except:  # noqa: E722
```

These silently swallow *all* exceptions including `KeyboardInterrupt` and `SystemExit`. Replace with `except Exception:` at minimum, or better yet, catch specific exceptions.

### 3. Legacy `typing` Imports

**File**: [check_vulnerabilities.py](file:///d:/PyAnsys/Repos/actions/check-vulnerabilities/check_vulnerabilities.py#L36)

```python
from typing import Any, Dict
```

Since the repo uses Python 3.11+ (and targets 3.12/3.13 in workflows), use built-in `dict` and `any` generics:

```diff
- from typing import Any, Dict
- def dict_hash(dictionary: Dict[str, Any]) -> str:
+ def dict_hash(dictionary: dict[str, any]) -> str:
```

### 4. `safety` Package Is End-of-Life — Migrate to `pip-audit`

**File**: [requirements.txt](file:///d:/PyAnsys/Repos/actions/check-vulnerabilities/requirements.txt)

The `safety` package (v2-3.x) has shifted to a freemium model and the free version has limited vulnerability database access. The industry has moved to [`pip-audit`](https://github.com/pypa/pip-audit), which:
- Uses the **OSV database** (free, maintained by Google)
- Is maintained by **PyPA** (official Python Packaging Authority)
- Directly integrates with pip's dependency resolver
- Supports SBOM generation (CycloneDX format)

> [!IMPORTANT]
> This is a significant change that would affect all downstream consumers of the `check-vulnerabilities` action. A migration plan and deprecation notice would be needed.

### 5. Missing `permissions` in `ci_cd_pr.yml` for Some Jobs

While the file has a top-level `permissions: contents: read`, individual jobs like `python-utilites-test` (line 360) lack explicit permission blocks. Since this job only needs `contents: read`, explicitly declaring it adds defense-in-depth — especially important since this is a **shared actions repo** where security is paramount.

### 6. `SECURITY.md` Could Be Enhanced

**File**: [SECURITY.md](file:///d:/PyAnsys/Repos/actions/SECURITY.md)

The current `SECURITY.md` is minimal. Consider adding:
- **Supported versions**: Which major versions receive security patches
- **Response timeline**: Expected SLA for vulnerability acknowledgment/fix
- **GitHub Security Advisories**: Mention that the repo uses GHSA
- **GPG signing information**: If releases are signed

---

## 🚀 Technology Modernization

### 7. Replace `flake8` + `isort` + `black` with `ruff`

**Files**: [.pre-commit-config.yaml](file:///d:/PyAnsys/Repos/actions/.pre-commit-config.yaml), [.flake8](file:///d:/PyAnsys/Repos/actions/.flake8)

The current setup uses **three separate tools** for linting and formatting:
- `black` for formatting
- `isort` for import sorting  
- `flake8` for linting

[Ruff](https://docs.astral.sh/ruff/) replaces all three with a **single, Rust-based tool** that is 10–100x faster:

```yaml
# Replace all three hooks with:
- repo: https://github.com/astral-sh/ruff-pre-commit
  rev: v0.11.13
  hooks:
    - id: ruff        # replaces flake8 + isort
      args: [--fix]
    - id: ruff-format # replaces black
```

This also lets you delete `.flake8` and consolidate configuration into `pyproject.toml` or `ruff.toml`.

### 8. Inconsistent Python Versions Across Workflows

| Workflow | `MAIN_PYTHON_VERSION` |
|---|---|
| `ci_cd_pr.yml` | `3.13` |
| `ci_cd_main.yml` | `3.12` |
| `ci_cd_night.yml` | `3.12` |
| `ci_cd_release.yml` | `3.12` |

Several action defaults also use `3.11`:
- `build-library/action.yml` → default `3.11`
- `tests-pytest/action.yml` → default `3.11`
- `release-pypi-public/action.yml` → default `3.11`
- `check-vulnerabilities/action.yml` → default `3.11`

> [!WARNING]
> The PR workflow uses 3.13 while main/nightly use 3.12. This can cause discrepancies where PRs pass but main fails (or vice versa). Standardize to `3.13` across all workflows and bump action defaults to at least `3.12`.

### 9. Replace `tomli` with Standard Library `tomllib` (Python 3.11+)

**File**: [parse_pr.py](file:///d:/PyAnsys/Repos/actions/python-utils/parse_pr.py#L27)

```python
import tomli
```

Since Python 3.11+, `tomllib` is in the standard library. This eliminates an external dependency:

```diff
- import tomli
+ import tomllib
  ...
- config = tomli.load(file)
+ config = tomllib.load(file)
```

### 10. Use `uv` for Pre-commit Tool Installation

Instead of `pip install pipx` → `pipx install poetry` chains in composite actions, consider using `uv tool install` which is already used for zizmor installation in [check-actions-security/action.yml](file:///d:/PyAnsys/Repos/actions/check-actions-security/action.yml#L91). This would make the approach consistent across all actions.

---

## 🏗️ Code Quality & Best Practices

### 11. `parse_pr.py` — Bug in `save_env_variable`

**File**: [parse_pr.py](file:///d:/PyAnsys/Repos/actions/python-utils/parse_pr.py#L50)

```python
file.write(f"{env_var_name}={env_var_value}")
# Missing trailing newline ^^^
```

Compare with `versions.py` line 108 which correctly appends `\n`:
```python
file.write(f"{var_name}={var_value}\n")
```

The missing newline could cause subsequent environment variables to be appended to the same line, leading to silent failures.

### 12. `parse_pr.py` — Buggy Sentinel Comparisons

**File**: [parse_pr.py](file:///d:/PyAnsys/Repos/actions/python-utils/parse_pr.py#L349-L352)

```python
if name != ("DNE" and ""):
```

This is a **logic bug**. `("DNE" and "")` evaluates to `""` (Python short-circuit evaluation), so this is equivalent to `if name != ""` — the `"DNE"` check is completely bypassed. Use:

```python
if name not in ("DNE", ""):
```

The same pattern appears on line 349: `if module != ("DNE" or "")` which evaluates to `if module != "DNE"`.

### 13. `rewrite_template()` Type Hints Are `None` Instead of `Optional[str]`

**File**: [parse_pr.py](file:///d:/PyAnsys/Repos/actions/python-utils/parse_pr.py#L488)

```python
def rewrite_template(template_path: None, file_name: None):
```

This should be:
```python
def rewrite_template(template_path: str | None = None, file_name: str | None = None):
```

### 14. `versions.py` — `assert` Used for Validation Logic

**File**: [versions.py](file:///d:/PyAnsys/Repos/actions/python-utils/versions.py#L199)

```python
assert version == match.group()
```

`assert` statements are stripped when Python runs with `-O` (optimized mode). Use an explicit `if` + `raise ValueError` for runtime validation.

### 15. `versions.py` — Unsafe `exit()` Calls

**File**: [versions.py](file:///d:/PyAnsys/Repos/actions/python-utils/versions.py#L216-L263)

Multiple `exit(1)` calls instead of `sys.exit(1)`. While functionally similar in scripts, `sys.exit()` is the standard and can be caught by test frameworks.

### 16. Typo in Job Name

**File**: [ci_cd_pr.yml](file:///d:/PyAnsys/Repos/actions/.github/workflows/ci_cd_pr.yml#L360)

```yaml
python-utilites-test:    # "utilites" → "utilities"
```

### 17. Duplicated Build-Backend Detection Logic

The following pattern is copy-pasted across at least 3 action files (`check-vulnerabilities`, `tests-pytest`, + more):

```bash
if [[ -f "pyproject.toml" ]] && grep -q 'build-backend = "poetry\.core\.masonry\.api"' "pyproject.toml"; then
  echo "BUILD_BACKEND=$(echo 'poetry')" >> $GITHUB_OUTPUT
elif [[ "$USE_UV" == 'true' ]]; then
  echo "BUILD_BACKEND=$(echo 'uv')" >> $GITHUB_OUTPUT
else
  echo "BUILD_BACKEND=$(echo 'pip')" >> $GITHUB_OUTPUT
fi
```

This should be extracted into a shared internal action (e.g., `_detect-build-backend`) to avoid drift and make maintenance easier.

### 18. Duplicated Virtual Environment Management

Similarly, the pattern of creating venvs, determining activation commands (`source .venv/bin/activate` vs `source .venv/scripts/activate`), and installing dependencies is duplicated across `tests-pytest`, `check-vulnerabilities`, and potentially other actions. This is another candidate for a shared internal action.

---

## 📦 Dependency Management

### 19. Pin `check-vulnerabilities` Requirements

**File**: [requirements.txt](file:///d:/PyAnsys/Repos/actions/check-vulnerabilities/requirements.txt)

Dependencies use range pins (`>=1.7,<2`) rather than exact pins. For CI tooling that runs in production pipelines, exact pinning with Dependabot updates provides better reproducibility:

```diff
- bandit>=1.7,<2
+ bandit==1.8.3
```

### 20. `check-jsonschema` Hook Could Validate Action Files Too

Currently [.pre-commit-config.yaml](file:///d:/PyAnsys/Repos/actions/.pre-commit-config.yaml#L32) only validates GitHub workflow files. Consider also adding `check-github-actions` to validate composite action `action.yml` files against the schema.

---

## 📊 Summary Table

| Priority | Area | Item | Effort |
|:---:|---|---|:---:|
| 🔴 | Security | Replace MD5 with SHA-256 | Low |
| 🔴 | Security | Migrate `safety` → `pip-audit` | High |
| 🟡 | Security | Fix bare `except:` clauses | Low |
| 🟡 | Code | Fix `save_env_variable` missing newline bug | Low |
| 🟡 | Code | Fix buggy sentinel comparisons in `parse_pr.py` | Low |
| 🟡 | Tech | Replace flake8/isort/black → ruff | Medium |
| 🟡 | Tech | Standardize Python versions across workflows | Low |
| 🟡 | Tech | Replace `tomli` → `tomllib` | Low |
| 🟢 | Code | Extract shared build-backend detection | Medium |
| 🟢 | Code | Extract shared venv management | Medium |
| 🟢 | Code | Fix type hints in `rewrite_template` | Low |
| 🟢 | Code | Replace `assert` with explicit validation | Low |
| 🟢 | Code | Replace `exit()` with `sys.exit()` | Low |
| 🟢 | Code | Fix "utilites" typo | Low |
| 🟢 | Security | Enhance SECURITY.md | Low |
| 🟢 | Deps | Pin check-vulnerabilities requirements exactly | Low |
