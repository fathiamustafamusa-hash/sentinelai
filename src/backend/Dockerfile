# ============================================================
# Stage 1: Builder - install dependencies
# ============================================================
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies (required for psycopg2 and asyncpg)
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry==2.1.4

# Copy dependency manifests
COPY pyproject.toml poetry.lock* ./

# Install dependencies (no venv, no root package)
RUN poetry config virtualenvs.create false \
    && poetry install --no-interaction --no-ansi --no-root --only main

# ============================================================
# Stage 2: Runtime - minimal production image
# ============================================================
FROM python:3.11-slim AS runtime

# Install runtime dependencies only (psycopg2 needs libpq)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user (security best practice)
RUN groupadd --system --gid 1001 appgroup \
    && useradd --system --uid 1001 --gid appgroup --create-home appuser

# Create /tmp with proper permissions (fixes "No usable temporary directory" error)
RUN mkdir -p /tmp && chmod 1777 /tmp && chown -R appuser:appgroup /tmp

WORKDIR /app

# Copy Python packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY --chown=appuser:appgroup ./app ./app
COPY --chown=appuser:appgroup ./run.py ./

# Switch to non-root user
USER appuser

# Set TMPDIR explicitly
ENV TMPDIR=/tmp
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Expose port
EXPOSE 8000

# Healthcheck using our /health endpoint
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Start command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
