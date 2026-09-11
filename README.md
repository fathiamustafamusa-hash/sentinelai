# 🛡️ SentinelAI — AI-Powered Enterprise SOC

[![CI](https://github.com/fathiamustafamusa-hash/sentinelai/actions/workflows/ci.yml/badge.svg)](https://github.com/fathiamustafamusa-hash/sentinelai/actions/workflows/ci.yml)
[![Security Scan](https://img.shields.io/badge/security-Bandit%20%7C%20pip--audit%20%7C%20Trivy-blueviolet)](https://github.com/fathiamustafamusa-hash/sentinelai/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![Coverage](https://img.shields.io/badge/coverage-82%25-brightgreen.svg)](#-testing)
[![Tests](https://img.shields.io/badge/tests-119%20passing-brightgreen.svg)](#-testing)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An integrated **Security Operations Center (SOC)** platform combining modern Blue Team tooling with AI-driven detection, IOC extraction, and MITRE ATT&CK mapping. Built with production-grade practices: async processing, layered security, and a full CI/CD pipeline.

## 📖 Table of Contents

- [Features](#-features)
- [Architecture](#-architecture)
- [Quick Start](#-quick-start)
- [Testing](#-testing)
- [API Reference](#-api-reference)
- [Tech Stack](#%EF%B8%8F-tech-stack)
- [Security](#-security)
- [Roadmap](#%EF%B8%8F-roadmap)

## ✨ Features

### 🔐 Authentication & Authorization
- JWT-based authentication with configurable expiry
- bcrypt password hashing with 72-byte handling
- Role-Based Access Control (RBAC): admin, analyst, viewer
- Protected routes via require_role dependency

### 🚨 Alert Management
- Full CRUD for security alerts
- Filter by severity, status, source
- Pagination (skip / limit)
- Auto timestamps (created_at, updated_at, resolved_at)
- Assign to analysts with automatic status transitions

### 🧠 Detection Engineering
- Automated IOC extraction: IPv4, domains, URLs, MD5/SHA1/SHA256, emails, CVEs, Windows paths, registry keys
- MITRE ATT&CK mapping with 16 cataloged techniques
- Keyword + source-based detection heuristics

### ⚡ Asynchronous Processing
- Celery + Redis for background tasks
- analyze_alert_ai task performs IOC extraction + MITRE mapping
- Task status polling via /api/tasks/{task_id}

### 📊 Statistics & Insights
- Aggregated metrics by severity, status, and source

## 🏗️ Architecture

SentinelAI follows a **layered architecture** designed for scalability, security, and async processing:

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Sources   │────▶│   FastAPI   │────▶│  PostgreSQL │
│ Wazuh,IDS.. │     │   Backend   │     │   Storage   │
└─────────────┘     └──────┬──────┘     └─────────────┘
                           │
                           ▼
                    ┌─────────────┐
                    │    Redis    │
                    │  Task Queue │
                    └──────┬──────┘
                           │
                           ▼
                    ┌─────────────┐
                    │   Celery    │
                    │   Worker    │
                    └─────────────┘
```

### 📐 Detailed Diagrams
- [**Overview**](docs/architecture/overview.md) — Component & layer diagram
- [**Data Flow**](docs/architecture/data-flow.md) — Alert lifecycle & async pipeline
- [**Auth Flow**](docs/architecture/auth-flow.md) — JWT & RBAC sequence
- [**Database**](docs/architecture/database.md) — ER diagram & indexes

## 🚀 Quick Start

**Prerequisites:** Docker 24+, Docker Compose v2

```bash
git clone https://github.com/fathiamustafamusa-hash/sentinelai.git
cd sentinelai
cp .env.example .env
docker compose up -d
```

**Access:**
- API: http://localhost:8000
- OpenAPI Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

See [**Local Setup Guide**](docs/deployment/local-setup.md) for hybrid development.

## 🧪 Testing

```bash
cd src/backend
poetry install --no-root
poetry run pytest tests/ -v --cov=app
```

**Results:**
- ✅ 119 tests passing
- ✅ 82% overall coverage
- ✅ 100% on ioc_extractor.py and mitre_mapper.py

## 🔌 API Reference

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | /api/auth/register | Register new user | Public |
| POST | /api/auth/login | Get JWT token | Public |
| GET | /api/auth/me | Current user profile | Any |
| GET | /health | Health check | Public |
| GET | /api/alerts/ | List alerts | Any |
| POST | /api/alerts/ | Create alert | Admin, Analyst |
| GET | /api/alerts/{id} | Get alert | Any |
| PATCH | /api/alerts/{id} | Update alert | Admin, Analyst |
| DELETE | /api/alerts/{id} | Delete alert | Admin |
| POST | /api/alerts/{id}/analyze | Queue AI analysis | Admin, Analyst |
| GET | /api/alerts/stats/overview | Statistics | Any |
| GET | /api/tasks/{task_id} | Celery task status | Any |

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| API | FastAPI, Uvicorn |
| Auth | python-jose (JWT), passlib + bcrypt |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL 15 |
| Cache / Broker | Redis 7 |
| Async Tasks | Celery |
| Validation | Pydantic v2 |
| Testing | pytest, pytest-cov, httpx |
| Linting | ruff, mypy |
| Security | Bandit, pip-audit, Trivy |
| Container | Docker, Docker Compose |
| CI/CD | GitHub Actions |

## 🔐 Security

This project treats security as a **first-class citizen**:

- **Static Analysis (SAST)**: Bandit scans every commit for Python vulnerabilities
- **Dependency Scanning**: pip-audit checks for known CVEs in dependencies
- **Container Scanning**: Trivy scans Docker images for OS + library vulnerabilities
- **Non-root Docker user** in production images
- **Multi-stage builds** to minimize attack surface
- **bcrypt** with 72-byte handling for password hashing
- **JWT** with timezone-aware expiry and signing
- **Pydantic v2** input validation on every endpoint
- **Secrets via environment variables** — never committed to Git

Please review our [**Security Policy**](SECURITY.md) for reporting vulnerabilities.

## 🗺️ Roadmap

- [x] Authentication + JWT + RBAC
- [x] Alert management (CRUD + filters + stats)
- [x] Celery async task pipeline
- [x] IOC extraction (8 types)
- [x] MITRE ATT&CK mapping (16 techniques)
- [x] Security scanning in CI (Bandit + pip-audit + Trivy)
- [x] Architecture diagrams (Mermaid)
- [x] Production deployment guides
- [ ] Sigma rule detection engine
- [ ] Wazuh / Suricata / Zeek ingestion
- [ ] React + TypeScript dashboard
- [ ] OpenAI + Ollama integration
- [ ] Helm chart for Kubernetes

## 🤝 Contributing

Contributions are welcome! Please read our [**Contributing Guide**](CONTRIBUTING.md) and [**Code of Conduct**](CODE_OF_CONDUCT.md) before opening a PR.

## 📜 License

MIT — see [LICENSE](LICENSE) for details.

## 👤 Author

**Mustafa Musa** — [@fathiamustafamusa-hash](https://github.com/fathiamustafamusa-hash)

---

⭐ If this project helped you, please give it a star!
