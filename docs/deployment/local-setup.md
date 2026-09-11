# 🖥️ Local Setup Guide

## Prerequisites

| Tool | Version | Install |
| :--- | :--- | :--- |
| Docker | 24+ | https://docs.docker.com/engine/install/ |
| Docker Compose | v2.20+ | Included with Docker Desktop |
| Python | 3.11+ | `sudo apt install python3.11` |
| Poetry | 1.7+ | `curl -sSL https://install.python-poetry.org | python3 -` |
| Git | 2.40+ | `sudo apt install git` |

## Quick Start (Docker)

```bash
# 1. Clone the repo
git clone https://github.com/fathiamustafamusa-hash/sentinelai.git
cd sentinelai

# 2. Create environment file
cp .env.example .env
# Edit .env with your values

# 3. Start all services
make up
# or: docker compose up -d

# 4. Verify health
curl http://localhost:8000/health
# → {"status":"healthy","postgres":"up","redis":"up"}
```

## Quick Start (Hybrid - for active development)

```bash
# 1. Start only PostgreSQL + Redis in Docker
docker compose up -d postgres redis

# 2. Configure .env for localhost access
sed -i "s/POSTGRES_HOST=postgres/POSTGRES_HOST=localhost/" .env
sed -i "s/REDIS_HOST=redis/REDIS_HOST=localhost/" .env

# 3. Install backend deps
cd src/backend
poetry install

# 4. Run backend with hot-reload
poetry run python run.py
```

## Common Tasks

| Task | Command |
| :--- | :--- |
| View logs | `docker compose logs -f backend` |
| Stop services | `make down` |
| Rebuild images | `make build` |
| Run tests | `make test` |
| Lint | `make lint` |
| Security scan | `make security` |
| Clean everything | `make clean` |

## Troubleshooting

### Port already in use
```bash
sudo ss -tulpn | grep -E ":(5432|6379|8000)"
# Kill the conflicting process or change the port in docker-compose.yml
```

### Database connection refused
```bash
docker compose ps  # Ensure postgres is "healthy"
docker compose logs postgres
```
