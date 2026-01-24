# ProInvestiX Enterprise - Deployment Guide

## 🚀 Quick Start

### Prerequisites
- Docker & Docker Compose
- Node.js 18+ (for frontend)
- Python 3.11+ (for backend)
- Rust 1.70+ (for desktop app)

### Local Development

```bash
# Clone repository
git clone https://github.com/proinvestix/proinvestix-enterprise.git
cd proinvestix-enterprise

# Start all services with Docker
cd proinvestix-deploy
cp .env.template .env
# Edit .env with your values
./scripts/deploy.sh deploy

# Access
# - Frontend: http://localhost:3000
# - API:      http://localhost:8000
# - API Docs: http://localhost:8000/docs
```

---

## 🏗️ Architecture

```
                    ┌─────────────┐
                    │   Nginx     │
                    │  (Reverse   │
                    │   Proxy)    │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  Frontend   │ │   API       │ │   Static    │
    │  (Next.js)  │ │  (FastAPI)  │ │   Files     │
    └─────────────┘ └──────┬──────┘ └─────────────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │  PostgreSQL │ │    Redis    │ │   S3/Minio  │
    │  (Database) │ │   (Cache)   │ │  (Storage)  │
    └─────────────┘ └─────────────┘ └─────────────┘
```

---

## 🚢 Deployment Options

### Option 1: Docker Compose (Self-hosted)

```bash
# Production deployment
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.yml down
```

### Option 2: Railway (Backend)

1. Install Railway CLI: `npm install -g @railway/cli`
2. Login: `railway login`
3. Deploy:
```bash
cd proinvestix-api
railway up
```

4. Set environment variables in Railway dashboard:
   - `DATABASE_URL`
   - `SECRET_KEY`
   - `CORS_ORIGINS`

### Option 3: Vercel (Frontend)

1. Install Vercel CLI: `npm install -g vercel`
2. Login: `vercel login`
3. Deploy:
```bash
cd proinvestix-frontend
vercel --prod
```

4. Set environment variables:
   - `NEXT_PUBLIC_API_URL`

### Option 4: Kubernetes

```bash
# Apply manifests
kubectl apply -f k8s/

# Check status
kubectl get pods -n proinvestix
```

---

## 🔧 Configuration

### Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | ✅ |
| `SECRET_KEY` | JWT signing key | ✅ |
| `REDIS_URL` | Redis connection string | ❌ |
| `CORS_ORIGINS` | Allowed origins | ✅ |
| `NEXT_PUBLIC_API_URL` | API URL for frontend | ✅ |

### Database Migrations

```bash
# Run migrations
docker-compose exec api alembic upgrade head

# Create new migration
docker-compose exec api alembic revision --autogenerate -m "description"

# Rollback
docker-compose exec api alembic downgrade -1
```

---

## 📊 Monitoring

### Health Checks

- **API Health:** `GET /health`
- **Database:** `GET /health/db`
- **Redis:** `GET /health/redis`

### Logging

Logs are stored in:
- Docker: `docker-compose logs`
- Files: `/var/log/proinvestix/`

### Metrics (Optional)

Enable Prometheus metrics by setting:
```env
ENABLE_METRICS=true
METRICS_PORT=9090
```

---

## 🔒 Security

### SSL/TLS

1. Generate certificates:
```bash
certbot certonly --standalone -d proinvestix.com -d www.proinvestix.com
```

2. Place certificates in `docker/nginx/ssl/`:
   - `fullchain.pem`
   - `privkey.pem`

### Secrets Management

For production, use:
- Docker Secrets
- HashiCorp Vault
- AWS Secrets Manager
- Railway/Vercel built-in secrets

---

## 🖥️ Desktop App Distribution

### Building

```bash
cd proinvestix-desktop

# Windows
npm run tauri:build:windows

# macOS
npm run tauri:build:mac

# Linux
npm run tauri:build:linux
```

### Auto-Updates

1. Set up update server endpoint
2. Sign binaries with private key
3. Host update JSON manifests

Update manifest example:
```json
{
  "version": "1.0.1",
  "notes": "Bug fixes and improvements",
  "pub_date": "2024-01-15T00:00:00Z",
  "platforms": {
    "windows-x86_64": {
      "url": "https://releases.proinvestix.com/1.0.1/ProInvestiX_1.0.1_x64-setup.exe",
      "signature": "..."
    }
  }
}
```

---

## 🔄 CI/CD Pipeline

The GitHub Actions workflow handles:

1. **On Pull Request:**
   - Run backend tests
   - Run frontend tests
   - Lint checks

2. **On Push to Main:**
   - Build Docker images
   - Push to container registry
   - Deploy to production

3. **On Release:**
   - Build desktop apps
   - Upload to release assets
   - Trigger auto-update

---

## 📝 Maintenance

### Backup

```bash
# Database backup
docker-compose exec db pg_dump -U proinvestix proinvestix > backup.sql

# Restore
docker-compose exec -T db psql -U proinvestix proinvestix < backup.sql
```

### Scaling

```bash
# Scale API replicas
docker-compose up -d --scale api=3
```

---

## 🆘 Troubleshooting

### Common Issues

1. **Database connection failed:**
   - Check `DATABASE_URL`
   - Ensure PostgreSQL is running

2. **CORS errors:**
   - Verify `CORS_ORIGINS` includes frontend URL

3. **JWT errors:**
   - Check `SECRET_KEY` matches across services

4. **Build failures:**
   - Clear caches: `docker system prune -a`
   - Rebuild: `docker-compose build --no-cache`

---

## 📞 Support

- **Documentation:** https://docs.proinvestix.com
- **Issues:** https://github.com/proinvestix/proinvestix-enterprise/issues
- **Email:** support@proinvestix.com

---

*ProInvestiX Enterprise - Deployment Guide v1.0*
