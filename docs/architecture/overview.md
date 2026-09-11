# 🏛️ Architecture Overview

## High-Level Diagram

```mermaid
graph TB
    W[Wazuh] --> API[FastAPI]
    S[Suricata] --> API
    Z[Zeek] --> API
    API --> Cache[(Redis)]
    API --> DB[(PostgreSQL)]
    Worker[Celery] --> Cache
    Worker --> DB
```

## Layers

| Layer | Responsibility | Tech |
| :--- | :--- | :--- |
| Ingestion | Receive alerts | FastAPI |
| Processing | Async analysis | Celery + Redis |
| Storage | Persistence | PostgreSQL |
| API | REST + JWT | FastAPI |
