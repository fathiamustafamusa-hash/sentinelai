# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Sigma rule detection engine
- Wazuh / Suricata / Zeek ingestion
- React + TypeScript dashboard
- OpenAI + Ollama integration
- Helm chart for Kubernetes

---

## [0.1.0] - 2026-09-11

First public release — production-ready backend with full CI/CD pipeline.

### Added

#### Authentication & Authorization
- JWT-based authentication (python-jose)
- bcrypt password hashing with 72-byte handling
- Role-Based Access Control: admin, analyst, viewer
- Protected routes via require_role dependency
- User registration and login endpoints

#### Alert Management
- Full CRUD API for security alerts
- Filtering by severity, status, and source
- Pagination with skip/limit
- Auto timestamps (created_at, updated_at, resolved_at)
- Alert assignment to analysts with status transitions
- Statistics endpoint (aggregations by severity/status/source)

#### Detection Engineering
- Automated IOC extraction (8 types):
  - IPv4 addresses (with private-IP filtering)
  - Domains
  - URLs
  - MD5 / SHA1 / SHA256 hashes
  - Email addresses
  - CVE identifiers
  - Windows file paths
  - Registry keys
- MITRE ATT&CK mapping with 16 cataloged techniques
- Keyword + source-based detection heuristics

#### Asynchronous Processing
- Celery worker with Redis broker
- analyze_alert_ai task (IOC + MITRE enrichment)
- Task status polling endpoint
- Risk score computation

#### Infrastructure
- Multi-stage Dockerfile (non-root user, minimal attack surface)
- docker-compose.yml for local development
- docker-compose.prod.yml for production (resource limits, replicas)
- Nginx reverse proxy configuration
- Makefile with developer shortcuts

#### Security
- Bandit SAST in CI
- pip-audit for dependency CVEs
- Trivy for container image scanning
- Security Policy (SECURITY.md)

#### Testing
- 119 unit tests (pytest)
- 82% overall code coverage
- 100% coverage on ioc_extractor.py and mitre_mapper.py

#### Documentation
- Professional README with badges and architecture
- Architecture diagrams (Mermaid): overview, data-flow, auth-flow, database
- Deployment guides (local-setup.md, production.md)
- Community files: CONTRIBUTING.md, CODE_OF_CONDUCT.md
- GitHub templates: PR, bug report, feature request

#### CI/CD
- GitHub Actions pipeline:
  - Lint (ruff) + Format + Type check (mypy)
  - Tests with coverage threshold (≥ 75%)
  - Security scan (Bandit + pip-audit + Trivy)
  - Docker build sanity check
- Dependabot for automated dependency updates
- Codecov integration for coverage tracking

---

[Unreleased]: https://github.com/fathiamustafamusa-hash/sentinelai/compare/v0.1.0...HEAD
[0.1.0]: https://github.com/fathiamustafamusa-hash/sentinelai/releases/tag/v0.1.0
