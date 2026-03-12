# Migrating from `safety` to `pip-audit`

## Team Presentation Summary

---

## The Problem

Our CI/CD vulnerability scanning relies on **`safety check`**, a tool that is now **deprecated, unsupported, and commercially restricted**. Continuing to use it puts our pipelines at risk of silent failures, stale vulnerability data, and potential license violations.

---

## Why We Must Move Away from `safety`

### 1. `safety check` is dead

- Deprecated in Safety 3.0.0 (January 2024)
- End-of-life was **June 2024** — over **18 months ago**
- No more security patches or database updates for the `check` command
- The replacement (`safety scan`) requires authentication — see below

### 2. Safety 3.x forces mandatory login

- `safety scan` requires a **registered SafetyCLI account**
- Without an API key, scans **fail or silently degrade**
- Every consuming repo would need a secret injected for authentication

### 3. Free tier is not viable for us

| Limitation | Impact |
|:---|:---|
| **100 scans/month** | Exhausted almost immediately across our repos |
| **Database updated once a month** | We could miss critical vulnerabilities for weeks |
| **Not licensed for commercial use** | Direct conflict with Ansys' commercial usage |

To unlock usable limits, Safety charges **$25/dev/month** (Team) or requires an enterprise contract.

---

## The Solution: `pip-audit`

`pip-audit` is the **official vulnerability scanning tool** from the [Python Packaging Authority (PyPA)](https://github.com/pypa) — the same organization that maintains `pip`, `setuptools`, and `PyPI` itself.

### Key advantages at a glance

| | `safety` (free tier) | `pip-audit` |
|:---|:---:|:---:|
| **Authentication** | Required (Safety 3+) | **None** |
| **Scan limits** | 100/month | **Unlimited** |
| **Database freshness** | Monthly updates | **Real-time** (OSV) |
| **Commercial license** | Not permitted | **Apache 2.0 — fully free** |
| **Maintainer** | SafetyCLI (commercial) | **PyPA** (community standard) |
| **Backers** | pyup.io | **Google + Trail of Bits** |
| **Same DB as GitHub Dependabot** | No | **Yes** |
| **Official GitHub Action** | No | **Yes** |
| **Cost** | $0–$25+/dev/month | **$0 forever** |

---

## Why `pip-audit` Is the Industry Standard

- **OSV database** — the same vulnerability database that powers **GitHub Dependabot** security alerts, giving us parity with GitHub's own scanning
- **No vendor lock-in** — open source, Apache 2.0 licensed, no accounts, no API keys
- **Real-time updates** — vulnerabilities appear as soon as they're published, not on a monthly cycle
- **PyPA-backed** — maintained by the official Python packaging team, ensuring long-term stability
- **Zero cost** — no per-developer pricing, no scan quotas, no enterprise negotiations

---

## Risk of Doing Nothing

| Risk | Likelihood | Impact |
|:---|:---:|:---:|
| `safety check` stops working entirely in a future Python/pip update | **High** | CI pipelines break across all consuming repos |
| Monthly DB updates miss a critical CVE | **Medium** | Vulnerable code ships to production |
| SafetyCLI enforces commercial license terms | **Low–Medium** | Legal/compliance exposure |
| Free-tier scan limit hit during release sprints | **High** | Vulnerability checks silently skipped |

---

## What Changes for Teams Consuming This Action

**Nothing.** The migration is handled inside the shared `check-vulnerabilities` action in `ansys/actions`. Downstream repos:

- Do **not** need to change their workflow files
- Do **not** need to add any new secrets or API keys
- Do **not** need to update any configuration
- Will get **better, faster, and more complete** vulnerability coverage automatically

---

## TL;DR

| Question | Answer |
|:---|:---|
| Why are we switching? | `safety check` has been **dead since June 2024** and the free tier **isn't licensed for commercial use** |
| What are we switching to? | `pip-audit` — the **official PyPA tool**, backed by Google, using the same DB as GitHub Dependabot |
| Does it cost anything? | **No.** Unlimited scans, no authentication, Apache 2.0 license |
| What do consuming teams need to do? | **Nothing.** The change is transparent |
| Is it better? | **Yes.** Real-time DB updates, no rate limits, no vendor lock-in |

---

## Sources

All claims about `safety` are sourced from Safety's own official documentation:

- [Safety 3.0.0 Changelog](https://github.com/pyupio/safety/blob/main/CHANGELOG.md)
- [Safety PyPI Page](https://pypi.org/project/safety/)
- [Safety Pricing](https://www.getsafety.com/pricing)
- [pip-audit Repository (PyPA)](https://github.com/pypa/pip-audit)
- [pip-audit GitHub Action](https://github.com/pypa/gh-action-pip-audit)
- [OSV Database](https://osv.dev/)
