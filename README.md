# 🛡️ SentinelAI — AI-Powered Enterprise SOC

[![CI](https://github.com/fathiamustafamusa-hash/sentinelai/actions/workflows/ci.yml/badge.svg)](https://github.com/fathiamustafamusa-hash/sentinelai/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/downloads/release/python-3110/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![Coverage](https://img.shields.io/badge/coverage-83%25-brightgreen.svg)](#-testing)
[![Tests](https://img.shields.io/badge/tests-119%20passing-brightgreen.svg)](#-testing)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

# 🛡️ SentinelAI — AI-Powered Enterprise SOC

[![CI](https://github.com/fathiamustafamusa-hash/sentinelai/actions/workflows/ci.yml/badge.svg)](https://github.com/fathiamustafamusa-hash/sentinelai/actions/workflows/ci.yml)
[![Python 3.11](https://img.shields.io/badge/python-3.11-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688.svg)](https://fastapi.tiangolo.com/)
[![Coverage](https://img.shields.io/badge/coverage-83%25-brightgreen.svg)](#testing)
[![Tests](https://img.shields.io/badge/tests-119%20passing-brightgreen.svg)](#testing)
[![Docker](https://img.shields.io/badge/docker-ready-blue.svg)](https://www.docker.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An integrated Security Operations Center (SOC) platform combining modern Blue Team tooling with AI-driven detection and enrichment. Built with FastAPI, PostgreSQL, Redis, Celery, and Docker.

## ✨ Features

### 🔐 Authentication & Authorization
- JWT-based authentication with token expiry
- bcrypt password hashing (72-byte truncation handling)
- Role-Based Access Control: admin, analyst, viewer
- Protected routes via require_role dependency

### 🚨 Alert Management
- Full CRUD for security alerts
- Filtering by severity, status, source
- Pagination with skip/limit
- Auto-timestamps (created_at, updated_at, resolved_at)
- Assign alerts to analysts with auto status transition

### 🧠 Detection Engineering
- Automated IOC extraction: IPs, domains, URLs, MD5/SHA1/SHA256, emails, CVEs, Windows paths, registry keys
- MITRE ATT&CK mapping with 16 techniques cataloged
- Keyword-based + source-based detection

### ⚡ Asynchronous Processing
- Celery + Redis for async task execution
- analyze_alert_ai task performs IOC extraction + MITRE mapping
- Task status polling via /api/tasks/{task_id}

### 📊 Statistics
- Aggregated metrics by severity, status, source

## 🏗️ Architecture

    SentinelAI/
    ├── src/backend/                # FastAPI application
    │   ├── app/
    │   │   ├── routers/            # API endpoints (auth, alerts, tasks)
    │   │   ├── services/           # Business logic
    │   │   ├── models/             # SQLAlchemy models
    │   │   ├── schemas/            # Pydantic schemas
    │   │   ├── dependencies/       # Auth dependencies
    │   │   ├── tasks/              # Celery tasks
    │   │   └── utils/              # Security utilities
    │   ├── tests/                  # 119 unit tests
    │   ├── Dockerfile              # Multi-stage build
    │   └── pyproject.toml          # Poetry dependencies
    ├── docker/                     # SOC tools configs
    ├── docs/                       # Documentation
    └── .github/workflows/ci.yml    # CI/CD pipeline

## 🚀 Quick Start

Prerequisites: Docker 24+, Docker Compose v2

    git clone https://github.com/fathiamustafamusa-hash/sentinelai.git
    cd sentinelai
    cp .env.example .env
    docker compose up -d

Access:
- API: http://localhost:8000
- OpenAPI Docs: http://localhost:8000/docs
- Health: http://localhost:8000/health

## 🧪 Testing

    cd src/backend
    poetry install --no-root
    poetry run pytest tests/ -v --cov=app

Results:
- 119 tests passing
- 83% code coverage
- 100% on ioc_extractor.py and mitre_mapper.py

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
| ORM | SQLAlchemy 2.0 (async + sync) |
| Database | PostgreSQL 15 |
| Cache / Broker | Redis 7 |
| Async Tasks | Celery |
| Validation | Pydantic v2 |
| Testing | pytest, pytest-cov, httpx |
| Linting | ruff, mypy |
| Container | Docker, Docker Compose |
| CI/CD | GitHub Actions |

## 🗺️ Roadmap

- [x] Authentication + JWT + RBAC
- [x] Alert management (CRUD + filters + stats)
- [x] Celery async task pipeline
- [x] IOC extraction
- [x] MITRE ATT&CK mapping
- [ ] Sigma rule detection engine
- [ ] Wazuh / Suricata / Zeek ingestion
- [ ] React + TypeScript dashboard
- [ ] OpenAI + Ollama integration
- [ ] AWS deployment

## 🔒 Security Best Practices

- Non-root Docker user
- Multi-stage Docker builds
- Secrets via environment variables
- bcrypt hashing with 72-byte handling
- JWT with timezone-aware expiry
- Input validation via Pydantic v2

## 📜 License

MIT — see LICENSE file.

## 👤 Author

Mustafa Musa — [@fathiamustafamusa-hash](https://github.com/fathiamustafamusa-hash)

---

## 🏛️ Architecture

SentinelAI follows a layered architecture designed for **scalability**, **security**, and **async processing**:

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

### 📐 Architecture Diagrams

- [**Overview**](docs/architecture/overview.md) — Component & layer diagram
- [**Data Flow**](docs/architecture/data-flow.md) — Alert lifecycle & async pipeline
- [**Auth Flow**](docs/architecture/auth-flow.md) — JWT & RBAC sequence
- [**Database**](docs/architecture/database.md) — ER diagram & indexes

### 🎯 Design Principles

- **Async-first**: Celery + Redis for long-running AI analysis
- **Stateless auth**: JWT tokens, no session store needed
- **Layered security**: Bandit SAST + pip-audit + Trivy in CI
- **Type-safe**: mypy + Pydantic v2 throughout
- **Observable**: structured logging + coverage reporting
