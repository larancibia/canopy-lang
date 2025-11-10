# Deployment Guide

## Overview

This guide covers deploying Canopy to various environments, from local development to production infrastructure.

## Table of Contents

- [Docker Deployment](#docker-deployment)
- [Environment Variables](#environment-variables)
- [Production Considerations](#production-considerations)
- [Cloud Platforms](#cloud-platforms)
- [Monitoring & Logging](#monitoring--logging)
- [Scaling Strategies](#scaling-strategies)
- [Security](#security)
- [Backup & Recovery](#backup--recovery)

## Docker Deployment

### Local Development

Start all services with Docker Compose:

```bash
docker-compose up
```

Services include:
- **canopy-api**: FastAPI backend (port 8000)
- **canopy-web**: React frontend (port 5173)
- **postgres**: PostgreSQL database (port 5432)
- **redis**: Redis cache (port 6379)

### Production Build

Build production images:

```bash
./scripts/build-docker.sh
```

Or manually:

```bash
# Build API
docker build -t canopy-api:latest --target production .

# Build Web
docker build -t canopy-web:latest --target production ./web
```

Start production services:

```bash
docker-compose --profile production up -d
```

### Docker Hub / GitHub Container Registry

**Tag and push images**:

```bash
# Tag images
docker tag canopy-api:latest your-registry/canopy-api:1.0.0
docker tag canopy-web:latest your-registry/canopy-web:1.0.0

# Push to registry
docker push your-registry/canopy-api:1.0.0
docker push your-registry/canopy-web:1.0.0
```

**Pull and run**:

```bash
# Pull images
docker pull your-registry/canopy-api:1.0.0
docker pull your-registry/canopy-web:1.0.0

# Run
docker-compose up -d
```

## Environment Variables

### Required Variables

Create `.env` file in production:

```bash
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
LOG_LEVEL=INFO

# Database
DATABASE_URL=postgresql://user:password@postgres:5432/canopy
DATABASE_POOL_SIZE=10
DATABASE_MAX_OVERFLOW=20

# Redis
REDIS_URL=redis://redis:6379
REDIS_PASSWORD=your_secure_password

# Security
SECRET_KEY=your-secret-key-min-32-chars
JWT_SECRET_KEY=your-jwt-secret-min-32-chars
JWT_ALGORITHM=HS256
JWT_EXPIRATION_MINUTES=60

# CORS
CORS_ORIGINS=https://app.canopy-lang.com,https://www.canopy-lang.com

# Data Providers
YAHOO_FINANCE_ENABLED=true
ALPACA_API_KEY=your_alpaca_key
ALPACA_SECRET_KEY=your_alpaca_secret
```

### Optional Variables

```bash
# Monitoring
SENTRY_DSN=https://your-sentry-dsn
SENTRY_ENVIRONMENT=production

# Email Notifications
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=your_sendgrid_api_key
SMTP_FROM_EMAIL=noreply@canopy-lang.com

# Rate Limiting
RATE_LIMIT_ENABLED=true
RATE_LIMIT_REQUESTS_PER_MINUTE=60

# Backtest Limits
MAX_BACKTEST_DURATION_DAYS=3650
DEFAULT_INITIAL_CAPITAL=10000
```

### Secrets Management

**AWS Secrets Manager**:

```python
import boto3
import json

def get_secret(secret_name):
    client = boto3.client('secretsmanager', region_name='us-east-1')
    response = client.get_secret_value(SecretId=secret_name)
    return json.loads(response['SecretString'])

secrets = get_secret('canopy/production')
DATABASE_URL = secrets['DATABASE_URL']
```

**Docker Secrets**:

```yaml
# docker-compose.yml
services:
  canopy-api:
    secrets:
      - db_password
      - jwt_secret

secrets:
  db_password:
    file: ./secrets/db_password.txt
  jwt_secret:
    file: ./secrets/jwt_secret.txt
```

## Production Considerations

### 1. Database Configuration

**PostgreSQL Optimization**:

```sql
-- Increase connection pool
ALTER SYSTEM SET max_connections = 200;

-- Optimize shared buffers
ALTER SYSTEM SET shared_buffers = '256MB';

-- Enable query optimization
ALTER SYSTEM SET effective_cache_size = '1GB';

-- Reload configuration
SELECT pg_reload_conf();
```

**Connection Pooling**:

```python
# Use SQLAlchemy with pgbouncer
DATABASE_URL = "postgresql://user:pass@pgbouncer:6432/canopy"

engine = create_engine(
    DATABASE_URL,
    pool_size=20,
    max_overflow=0,
    pool_pre_ping=True,
    pool_recycle=3600
)
```

### 2. Redis Configuration

```bash
# redis.conf
maxmemory 256mb
maxmemory-policy allkeys-lru
save 900 1
save 300 10
appendonly yes
```

### 3. API Configuration

**Production settings**:

```python
# config.py
class ProductionSettings(Settings):
    debug: bool = False
    enable_auth: bool = True
    rate_limit_enabled: bool = True
    log_level: str = "WARNING"
    cors_origins: List[str] = ["https://app.canopy-lang.com"]
```

**Gunicorn Configuration**:

```python
# gunicorn.conf.py
bind = "0.0.0.0:8000"
workers = 4  # 2-4 x CPU cores
worker_class = "uvicorn.workers.UvicornWorker"
keepalive = 120
timeout = 120
max_requests = 1000
max_requests_jitter = 50
accesslog = "/var/log/gunicorn/access.log"
errorlog = "/var/log/gunicorn/error.log"
loglevel = "info"
```

Run with Gunicorn:

```bash
gunicorn canopy.api.main:app -c gunicorn.conf.py
```

### 4. Nginx Configuration

```nginx
# nginx.conf
upstream canopy_api {
    server canopy-api:8000;
}

server {
    listen 80;
    server_name api.canopy-lang.com;

    # Redirect HTTP to HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name api.canopy-lang.com;

    ssl_certificate /etc/letsencrypt/live/api.canopy-lang.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.canopy-lang.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # API proxy
    location / {
        proxy_pass http://canopy_api;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # Timeouts
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }

    # Health check
    location /health {
        access_log off;
        proxy_pass http://canopy_api;
    }
}
```

## Cloud Platforms

### AWS (Elastic Beanstalk / ECS)

#### Elastic Beanstalk

1. **Install EB CLI**:
```bash
pip install awsebcli
```

2. **Initialize**:
```bash
eb init -p docker canopy-api
```

3. **Create environment**:
```bash
eb create canopy-production
```

4. **Deploy**:
```bash
eb deploy
```

#### ECS with Fargate

**Task Definition** (`task-definition.json`):

```json
{
  "family": "canopy-api",
  "networkMode": "awsvpc",
  "requiresCompatibilities": ["FARGATE"],
  "cpu": "1024",
  "memory": "2048",
  "containerDefinitions": [
    {
      "name": "canopy-api",
      "image": "your-registry/canopy-api:latest",
      "portMappings": [
        {
          "containerPort": 8000,
          "protocol": "tcp"
        }
      ],
      "environment": [
        {"name": "LOG_LEVEL", "value": "INFO"}
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:secretsmanager:region:account:secret:canopy/db"
        }
      ],
      "logConfiguration": {
        "logDriver": "awslogs",
        "options": {
          "awslogs-group": "/ecs/canopy-api",
          "awslogs-region": "us-east-1",
          "awslogs-stream-prefix": "ecs"
        }
      }
    }
  ]
}
```

### Google Cloud Platform (Cloud Run)

1. **Build and push image**:
```bash
gcloud builds submit --tag gcr.io/PROJECT_ID/canopy-api
```

2. **Deploy to Cloud Run**:
```bash
gcloud run deploy canopy-api \
  --image gcr.io/PROJECT_ID/canopy-api \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --set-env-vars DATABASE_URL=postgres://... \
  --memory 2Gi \
  --cpu 2
```

### DigitalOcean

1. **Create App Platform app**:
```bash
doctl apps create --spec app-spec.yaml
```

2. **App Spec** (`app-spec.yaml`):
```yaml
name: canopy
services:
- name: api
  github:
    repo: your-org/canopy-lang
    branch: main
    deploy_on_push: true
  dockerfile_path: Dockerfile
  http_port: 8000
  instance_count: 2
  instance_size_slug: professional-s
  envs:
  - key: DATABASE_URL
    scope: RUN_TIME
    value: ${db.DATABASE_URL}
  - key: REDIS_URL
    scope: RUN_TIME
    value: ${redis.REDIS_URL}

databases:
- name: db
  engine: PG
  version: "15"

- name: redis
  engine: REDIS
  version: "7"
```

### Heroku

1. **Create app**:
```bash
heroku create canopy-api
```

2. **Add buildpacks**:
```bash
heroku buildpacks:add heroku/python
```

3. **Set config**:
```bash
heroku config:set SECRET_KEY=your-secret
heroku config:set DATABASE_URL=postgres://...
```

4. **Deploy**:
```bash
git push heroku main
```

5. **Scale**:
```bash
heroku ps:scale web=2
```

## Monitoring & Logging

### Logging

**Structured logging**:

```python
# src/canopy/utils/logger.py
import logging
import json
from datetime import datetime

class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_obj = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
        }
        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_obj)

# Configure
logger = logging.getLogger("canopy")
handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)
logger.setLevel(logging.INFO)
```

### Monitoring

**Health Check Endpoint**:

```python
@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "database": check_database(),
        "redis": check_redis(),
        "disk_space": check_disk_space(),
    }
```

**Prometheus Metrics**:

```python
from prometheus_client import Counter, Histogram, make_asgi_app

backtest_counter = Counter('backtests_total', 'Total backtests')
backtest_duration = Histogram('backtest_duration_seconds', 'Backtest duration')

# Add Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)
```

**Sentry Integration**:

```python
import sentry_sdk
from sentry_sdk.integrations.fastapi import FastApiIntegration

sentry_sdk.init(
    dsn=settings.sentry_dsn,
    environment=settings.environment,
    integrations=[FastApiIntegration()],
    traces_sample_rate=0.1,
)
```

## Scaling Strategies

### Horizontal Scaling

**Multiple API instances**:

```yaml
# docker-compose.yml
services:
  canopy-api:
    deploy:
      replicas: 3
      resources:
        limits:
          cpus: '1'
          memory: 2G
```

**Load Balancer**:

```nginx
upstream canopy_backend {
    least_conn;
    server canopy-api-1:8000;
    server canopy-api-2:8000;
    server canopy-api-3:8000;
}
```

### Vertical Scaling

**Increase resources**:

```bash
# Docker
docker run -m 4g --cpus=2 canopy-api

# Kubernetes
resources:
  requests:
    memory: "2Gi"
    cpu: "1000m"
  limits:
    memory: "4Gi"
    cpu: "2000m"
```

### Database Scaling

**Read Replicas**:

```python
# Write to primary
write_engine = create_engine(PRIMARY_DB_URL)

# Read from replicas
read_engine = create_engine(REPLICA_DB_URL)
```

**Connection Pooling**:

```bash
# Install pgbouncer
docker run -d -p 6432:6432 pgbouncer/pgbouncer
```

### Caching

**Redis Caching**:

```python
import redis
from functools import wraps

redis_client = redis.Redis.from_url(settings.redis_url)

def cache(ttl=300):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            cache_key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            result = await func(*args, **kwargs)
            redis_client.setex(cache_key, ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

## Security

### HTTPS/TLS

**Let's Encrypt with Certbot**:

```bash
# Install certbot
apt-get install certbot python3-certbot-nginx

# Get certificate
certbot --nginx -d api.canopy-lang.com

# Auto-renewal
certbot renew --dry-run
```

### API Security

**Rate Limiting**:

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.get("/api/backtests")
@limiter.limit("60/minute")
async def list_backtests(request: Request):
    pass
```

**API Key Authentication**:

```python
from fastapi import Security, HTTPException
from fastapi.security.api_key import APIKeyHeader

api_key_header = APIKeyHeader(name="X-API-Key")

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key not in settings.api_keys:
        raise HTTPException(status_code=403, detail="Invalid API key")
    return api_key
```

### Database Security

```python
# Use parameterized queries
query = "SELECT * FROM users WHERE id = %s"
cursor.execute(query, (user_id,))

# Encrypt sensitive fields
from cryptography.fernet import Fernet

cipher = Fernet(settings.encryption_key)
encrypted_data = cipher.encrypt(sensitive_data.encode())
```

## Backup & Recovery

### Database Backups

**Automated backups**:

```bash
#!/bin/bash
# scripts/backup-db.sh

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="canopy_backup_${TIMESTAMP}.sql"

pg_dump -h localhost -U canopy canopy > /backups/${BACKUP_FILE}

# Upload to S3
aws s3 cp /backups/${BACKUP_FILE} s3://canopy-backups/

# Keep only last 30 days
find /backups -name "canopy_backup_*.sql" -mtime +30 -delete
```

**Cron job**:

```bash
# Run daily at 2 AM
0 2 * * * /scripts/backup-db.sh
```

### Restore

```bash
# Restore from backup
pg_restore -h localhost -U canopy -d canopy /backups/canopy_backup_20240115.sql
```

## Troubleshooting

### High Memory Usage

```bash
# Check memory
docker stats

# Adjust Python memory
export PYTHONMALLOC=malloc
```

### High CPU Usage

```bash
# Profile application
py-spy top --pid <pid>

# Check slow queries
SELECT * FROM pg_stat_activity WHERE state = 'active';
```

### Connection Pool Exhaustion

```python
# Increase pool size
engine = create_engine(url, pool_size=20, max_overflow=40)

# Add connection health checks
engine = create_engine(url, pool_pre_ping=True)
```

## Rollback Strategy

```bash
# Keep previous version
docker tag canopy-api:latest canopy-api:previous

# Deploy new version
docker pull canopy-api:latest
docker-compose up -d

# Rollback if needed
docker tag canopy-api:previous canopy-api:latest
docker-compose up -d
```

## Checklist

### Pre-Deployment

- [ ] Run all tests
- [ ] Update version number
- [ ] Build Docker images
- [ ] Test Docker images locally
- [ ] Update environment variables
- [ ] Database migrations
- [ ] Backup database
- [ ] Update documentation

### Post-Deployment

- [ ] Verify health endpoints
- [ ] Check logs for errors
- [ ] Monitor metrics
- [ ] Test critical endpoints
- [ ] Verify database connectivity
- [ ] Check Redis connectivity
- [ ] Update DNS if needed
- [ ] Notify team

## Next Steps

- Set up monitoring dashboards (Grafana, Datadog)
- Configure alerting (PagerDuty, Opsgenie)
- Implement blue-green deployment
- Set up CI/CD pipeline (GitHub Actions, GitLab CI)
- Configure autoscaling
- Implement disaster recovery plan
