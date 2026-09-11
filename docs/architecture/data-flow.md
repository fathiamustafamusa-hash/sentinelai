# 🔄 Data Flow

## Alert Lifecycle

```mermaid
sequenceDiagram
    participant SRC as Source
    participant API as FastAPI
    participant DB as PostgreSQL
    participant W as Celery
    SRC->>API: POST /api/alerts
    API->>DB: INSERT alert
    API-->>SRC: 201 Created
    W->>DB: SELECT alert
    W->>DB: UPDATE enriched
```

## Storage Strategy

| Data | Storage | Retention |
| :--- | :--- | :--- |
| Alerts | PostgreSQL | 90 days |
| Raw JSON | JSONB | 30 days |
| Task cache | Redis | 1 hour |
| Tokens | JWT | 30 min |
