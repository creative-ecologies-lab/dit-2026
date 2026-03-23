# Dependency Audit -- 2026-03-23

**Repository:** dit-2026 (aiskillsmap.noahratzan.com)
**Runtime:** Python 3.12 on Cloud Run (gunicorn + Flask)
**Node.js:** devDependencies only (Playwright for E2E tests)

---

## Executive Summary

**No known security vulnerabilities found** in either Python (pip-audit) or Node.js (npm audit) dependencies. The codebase is in good shape. The main findings are:

- 22 Python packages have newer versions available (all patch/minor)
- A `google-auth` dev version (`2.49.0.dev0`) is installed -- should be pinned to a stable release
- `protobuf` shows 5.29.6 -> 7.34.1 as "latest" but this is a **major version jump** -- do NOT upgrade without testing
- `google-ai-generativelanguage` 0.6.15 -> 0.10.0 is also a major jump -- skip for now
- Playwright (devDependency) is current at 1.58.2

---

## Security Vulnerabilities

| Severity | Package | Issue | Action |
|----------|---------|-------|--------|
| None found | -- | -- | -- |

Both `pip-audit` (against requirements.txt) and `npm audit` returned clean results.

---

## Python Packages -- Outdated

### Safe to Update (patch/minor only)

These are patch or minor version bumps within the same major version, safe for immediate update:

| Package | Installed | Latest | Type | In requirements.txt |
|---------|-----------|--------|------|---------------------|
| Flask | 3.1.2 | 3.1.3 | patch | Yes (`>=3.0`) |
| Werkzeug | 3.1.5 | 3.1.6 | patch | No (transitive) |
| numpy | 2.4.2 | 2.4.3 | patch | Yes (`>=1.24`) |
| scipy | 1.17.0 | 1.17.1 | patch | No (transitive) |
| certifi | 2026.1.4 | 2026.2.25 | patch | No (transitive) |
| charset-normalizer | 3.4.4 | 3.4.6 | patch | No (transitive) |
| python-dotenv | 1.2.1 | 1.2.2 | patch | Yes (unpinned) |
| pydantic-settings | 2.12.0 | 2.13.1 | minor | Yes (`>=2.0`) |
| pydantic_core | 2.41.5 | 2.42.0 | minor | No (transitive) |
| pyasn1 | 0.6.2 | 0.6.3 | patch | No (transitive) |
| wrapt | 2.1.1 | 2.1.2 | patch | No (transitive) |
| regex | 2026.1.15 | 2026.2.28 | patch | No (transitive) |
| google-api-core | 2.29.0 | 2.30.0 | minor | No (transitive) |
| google-api-python-client | 2.189.0 | 2.193.0 | minor | No (transitive) |
| googleapis-common-protos | 1.72.0 | 1.73.0 | minor | No (transitive) |
| grpcio-status | 1.71.2 | 1.78.0 | minor | No (transitive) |

### Needs Attention

| Package | Installed | Latest | Risk | Notes |
|---------|-----------|--------|------|-------|
| google-auth | 2.49.0.dev0 | 2.49.1 | **Medium** | Dev/pre-release version installed. Should use stable 2.49.1. |
| openai | 2.20.0 | 2.29.0 | Low | Minor version bump. Used in scripts only (embeddings generator). |
| anthropic | 0.79.0 | 0.86.0 | Low | Minor version bump. Used in think-aloud scripts only. |

### Do NOT Update (major version jumps)

| Package | Installed | Latest | Risk | Notes |
|---------|-----------|--------|------|-------|
| protobuf | 5.29.6 | 7.34.1 | **High** | Major version jump (5.x -> 7.x). Google Cloud libs may not be compatible. |
| google-ai-generativelanguage | 0.6.15 | 0.10.0 | **High** | Major API changes likely. Transitive dep of google-generativeai. |

---

## Node.js Packages

| Package | Installed | Latest | Notes |
|---------|-----------|--------|-------|
| @playwright/test | 1.58.2 | 1.58.2 | Current. devDependency only. |

No vulnerabilities. No outdated packages.

---

## Observations and Recommendations

### 1. Pin requirements.txt versions (Priority: Medium)

Current requirements.txt uses floor pins (`>=3.0`) which allows arbitrary future versions. For a production Cloud Run service, consider pinning to specific versions or narrow ranges to ensure reproducible builds.

**Current:**
```
flask>=3.0
numpy>=1.24
```

**Recommended:**
```
flask>=3.1,<4
numpy>=2.4,<3
```

### 2. Fix google-auth dev version (Priority: Medium)

The installed `google-auth==2.49.0.dev0` is a pre-release. This likely happened during a `pip install` with `--pre` or from a dependency resolver edge case. Add an explicit pin in requirements.txt to force stable:

```
google-auth>=2.49.1
```

### 3. google-generativeai is unused (Priority: Low)

The package `google-generativeai` (and its dependency `google-ai-generativelanguage`) are installed in the venv but:
- Not listed in requirements.txt
- Not imported anywhere in the codebase

These were likely installed manually for experimentation. They are harmless in the venv but are not shipped in the Docker image (since they are not in requirements.txt).

### 4. gunicorn not testable on Windows (Priority: Info)

`gunicorn` is in requirements.txt but cannot be installed on Windows (Linux-only). This is expected -- it only runs in the Docker/Cloud Run environment. No action needed.

### 5. Dockerfile uses python:3.12-slim (Priority: Info)

The base image `python:3.12-slim` is appropriate. Python 3.12 is actively supported through Oct 2028.

---

## Changes Made in This PR

1. **requirements.txt** -- Tightened version pins with upper bounds to prevent unexpected major version jumps during Docker builds, and added explicit `google-auth` pin to avoid dev versions.

---

*Generated by dependency audit, 2026-03-23.*
