# 🗄️ Database Schema

## ER Diagram

```mermaid
erDiagram
    USERS {
        int id PK
        string username UK
        string email UK
        string role
    }
    ALERTS {
        int id PK
        string title
        string severity
        int assigned_to FK
    }
    USERS ||--o{ ALERTS : assigned_to
```

## Indexes

| Table | Column | Type |
| :--- | :--- | :--- |
| users | username | UNIQUE |
| users | email | UNIQUE |
| alerts | status | B-tree |
| alerts | severity | B-tree |
| alerts | created_at | DESC |
