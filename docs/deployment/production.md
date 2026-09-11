# 🚀 Production Deployment Guide

## Architecture in Production

```
                    ┌──────────────────┐
                    │   Internet       │
                    └────────┬─────────┘
                             │ 443/80
                    ┌────────▼─────────┐
                    │   Nginx          │  (TLS termination)
                    │   reverse proxy  │
                    └────────┬─────────┘
                             │ 127.0.0.1:8000
              ┌──────────────┼──────────────┐
              │              │              │
        ┌─────▼─────┐  ┌─────▼─────┐  ┌─────▼─────┐
        │ Backend #1│  │ Backend #2│  │  Nginx    │
        └─────┬─────┘  └─────┬─────┘  └───────────┘
              │              │
              └──────┬───────┘
                     │
              ┌──────▼───────┐
              │  PostgreSQL  │  (internal only)
              └──────────────┘
```

## Deployment Options

### Option 1: Single VPS (DigitalOcean / Hetzner / AWS EC2)

**Pros**: Cheap ($5-20/mo), full control
**Cons**: You manage everything

```bash
# On a fresh Ubuntu 22.04 server:

# 1. Install Docker
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER

# 2. Clone the repo
git clone https://github.com/fathiamustafamusa-hash/sentinelai.git
cd sentinelai

# 3. Create .env.prod
cp .env.prod.example .env.prod
nano .env.prod  # fill in secure values

# 4. Generate strong secrets
echo "SECRET_KEY=$(openssl rand -hex 32)" >> .env.prod
echo "POSTGRES_PASSWORD=$(openssl rand -base64 32)" >> .env.prod
echo "REDIS_PASSWORD=$(openssl rand -base64 32)" >> .env.prod

# 5. Obtain TLS cert (Lets Encrypt)
sudo apt install certbot
sudo certbot certonly --standalone -d your-domain.com
sudo cp /etc/letsencrypt/live/your-domain.com/fullchain.pem docker/nginx/certs/
sudo cp /etc/letsencrypt/live/your-domain.com/privkey.pem docker/nginx/certs/

# 6. Start production stack
make prod-up

# 7. Setup auto-renewal
(crontab -l 2>/dev/null; echo "0 3 * * * certbot renew --quiet && docker compose -f docker-compose.yml -f docker-compose.prod.yml restart nginx") | crontab -
```

### Option 2: AWS ECS + RDS + ElastiCache

**Pros**: Managed, auto-scaling, high availability
**Cons**: More complex, higher cost

Components:
- **ECR**: Docker image registry
- **ECS Fargate**: Run backend + celery containers
- **RDS PostgreSQL**: Managed database (Multi-AZ)
- **ElastiCache Redis**: Managed cache
- **ALB**: Application Load Balancer
- **Secrets Manager**: Store secrets
- **CloudWatch**: Logs + metrics

Steps (high-level):
1. Build and push image to ECR
2. Create RDS instance (private subnet)
3. Create ElastiCache cluster (private subnet)
4. Store secrets in Secrets Manager
5. Create ECS Task Definition (backend + celery)
6. Create ECS Service with ALB
7. Configure security groups (least privilege)
8. Setup CloudWatch alarms

## Secrets Management

**Never commit secrets to Git.**

### Local / VPS: .env.prod file
```bash
chmod 600 .env.prod
```

### AWS: Secrets Manager
```bash
aws secretsmanager create-secret \\
  --name sentinelai/prod \\
  --secret-string file://secrets.json
```

### Kubernetes: External Secrets Operator
Use External Secrets to sync from AWS Secrets Manager.

## Monitoring & Observability

| Concern | Tool | Setup |
| :--- | :--- | :--- |
| Logs | Loki + Grafana | Add to compose stack |
| Metrics | Prometheus + Grafana | Add /metrics endpoint |
| Uptime | Uptime Kuma | External monitor |
| Errors | Sentry | `pip install sentry-sdk` |

## Backups

### PostgreSQL
```bash
# Daily backup script (add to cron)
docker exec sentinel-postgres pg_dump -U sentinel_user sentinel_soc | \\
  gzip > /backups/sentinelai-$(date +%Y%m%d).sql.gz

# Keep last 30 days
find /backups -name "*.sql.gz" -mtime +30 -delete
```

### Redis (RDB snapshots)
```bash
docker exec sentinel-redis redis-cli -a $REDIS_PASSWORD BGSAVE
```
