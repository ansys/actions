# Why We Replaced `safety` with `pip-audit`

All evidence below is sourced directly from Safety's own official pages and changelogs.

---

## 1. `safety check` Is Deprecated and Past End-of-Life

The action was calling `safety check`. From Safety's own
[3.0.0 changelog](https://github.com/pyupio/safety/blob/main/CHANGELOG.md) (released January 2024):

> "Add deprecation notice to `safety check` command... The check command will continue
> receiving **maintenance support until June 2024**."

As of today (February 2026), `safety check` has been **unsupported for over 18 months**.
There is no upgrade path to the replacement command (`safety scan`) without account
authentication — see point 2.

---

## 2. Safety 3.x Requires Authentication — Breaking Unauthenticated CI/CD

From the [Safety 3.0.0 changelog](https://github.com/pyupio/safety/blob/main/CHANGELOG.md):

> "Added auth commands, enabling new browser-based authentication of Safety CLI."

From the [Safety PyPI page](https://pypi.org/project/safety/):

> "If not authenticated, Safety will prompt for account creation or login."
> "Run `safety auth` to check authentication status."

The new `safety scan` command requires a registered Safety account. Without a valid
API key injected as a secret in every consumer CI/CD pipeline, scans either fail
outright or silently degrade to the heavily restricted free tier (see point 3).

---

## 3. The Free Database Is Rate-Limited, Stale, and Not Licensed for Commercial Use

From the [Safety 2.0.0 changelog](https://github.com/pyupio/safety/blob/main/CHANGELOG.md):

> "The free version of the Safety vulnerability database is downloaded from a public
> S3 bucket (via PyUp.io)... this free database is **only updated once a month** and is
> **not licensed for commercial use**."

From the [Safety PyPI page](https://pypi.org/project/safety/):

> "This plan is limited to a single user and **is not recommended for commercial
> purposes**."

From the [Safety pricing page](https://www.getsafety.com/pricing):

| Plan | DB coverage | Scans/month | Cost |
|---|---|:---:|---|
| Free | Public vulnerability data only | **100** | $0 |
| Team | **4× more** than public databases | 5,000 | $25/dev/month |
| Enterprise | Full database | 20,000 | Contact sales |

`ansys/actions` is a **shared commercial repo** consumed across many Ansys projects.
100 scans/month is exhausted rapidly, and the free tier is explicitly not licensed for
commercial use.

---

## 4. `pip-audit` Has None of These Problems

| Criteria | `safety` (free tier) | `pip-audit` |
|---|---|---|
| Authentication required | **Yes** (Safety 3+) | No |
| `check` command supported | **No** (EOL June 2024) | N/A |
| Database update frequency | **Monthly** (free tier) | Real-time (PyPI / OSV) |
| Commercial use | **Not licensed** | Apache 2.0 — fully free |
| Maintained by | SafetyCLI (commercial company) | **PyPA** (Python Packaging Authority) |
| Scan limits | **100/month** (free tier) | Unlimited |
| Backed by | pyup.io / SafetyCLI | **Google + Trail of Bits** |
| Used by GitHub Dependabot | No | **Yes** (same OSV database) |
| Official GitHub Action | No | **Yes** (`pypa/gh-action-pip-audit`) |

`pip-audit` is the **official PyPA tool** for auditing Python environments. It uses the
[OSV database](https://osv.dev/) — the same database that powers GitHub's own Dependabot
security alerts — with no account required, no rate limits, and no commercial
restrictions.

---

## 5. Sources

- Safety 3.0.0 release notes: <https://github.com/pyupio/safety/blob/main/CHANGELOG.md>
- Safety PyPI page: <https://pypi.org/project/safety/>
- Safety pricing page: <https://www.getsafety.com/pricing>
- pip-audit repository: <https://github.com/pypa/pip-audit>
- pip-audit GitHub Action: <https://github.com/pypa/gh-action-pip-audit>
- OSV database: <https://osv.dev/>
