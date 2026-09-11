# 📦 Deployment Documentation

Complete guides for deploying SentinelAI in various environments.

## Guides

| Guide | Description | When to use |
| :--- | :--- | :--- |
| [Local Setup](local-setup.md) | Docker-based local development | First-time setup |
| [Production](production.md) | VPS / AWS deployment | Going live |
| [Architecture](../architecture/overview.md) | System design | Understanding the code |

## Deployment Decision Tree

```mermaid
flowchart TD
    A[Where to deploy?] --> B{Budget?}
    B -->|Low<br/>$5-20/mo| C[Single VPS<br/>DigitalOcean/Hetzner]
    B -->|Medium<br/>$50-200/mo| D[AWS ECS Fargate]
    B -->|Enterprise| E[Kubernetes EKS]

    C --> F[Follow production.md<br/>Option 1]
    D --> G[Follow production.md<br/>Option 2]
    E --> H[Use Helm charts<br/>roadmap]
```

## Environment Matrix

| Env | Compose files | Secrets | Data |
| :--- | :--- | :--- | :--- |
| Local dev | `docker-compose.yml` | `.env` | Local volumes |
| Local prod | `docker-compose.yml` + `docker-compose.prod.yml` | `.env.prod` | Named volumes |
| Cloud | Kubernetes / ECS | Secrets Manager | Managed services |
