# Changelog

## Unreleased — hardening/audit-1

- Added the owner-approved proprietary license: All Rights Reserved.

- Added authenticated task ownership, constant-time API key comparison, request-size limits, rate limiting, and a readiness endpoint.
- Added safer workspace path checks, file/count limits, Python process limits, SSRF checks, redirect blocking, and worker-side webhook enforcement.
- Added candidate skill hashing, HTTPS/host controls, pinned-source checks, explicit approval CLI, and audit logging.
- Added Docker Compose secrets, Redis authentication, healthchecks, non-root containers, read-only filesystems, resource limits, and `env_file` propagation.
- Added Alembic initial migration, development-only `create_all`, CI, Ruff, pip-audit, coverage, Makefile, and pre-commit configuration.
- Moved documentation and model scripts into `docs/` and `scripts/`.

### Breaking changes

- Production startup now requires non-placeholder `API_KEYS`; use `ENV=dev` only for local development.
- Compose now requires `POSTGRES_PASSWORD` and `REDIS_PASSWORD` in `.env`.
- Production database creation must run through Alembic migrations.
- GitHub/GitLab skill imports require a pinned commit SHA and are never approved automatically.
