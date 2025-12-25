# SEFCNet Deployment Guide

Complete guide for deploying SEFCNet to production.

## Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# 1. Copy environment file
cp .env.example .env

# 2. Edit .env with your configuration
# Important: Change SEFCNET_JWT_SECRET to a secure random string

# 3. Start all services
docker-compose up -d

# 4. Check logs
docker-compose logs -f sefcnet-api

# 5. Access the API
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Dashboard: http://localhost:8501
```

### Option 2: Local Development

#### Windows:
```powershell
.\scripts\start_server.ps1
```

#### Linux/macOS:
```bash
chmod +x scripts/start_server.sh
./scripts/start_server.sh
```

#### Manual:
```bash
# 1. Create virtual environment
python -m venv venv

# 2. Activate virtual environment
# Windows:
.\venv\Scripts\Activate.ps1
# Linux/macOS:
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Copy and configure environment
cp .env.example .env
# Edit .env with your settings

# 5. Start server
python start.py
```

## Environment Configuration

### Required Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `HOST` | Server host | `0.0.0.0` |
| `PORT` | Server port | `8000` |
| `DEBUG` | Debug mode | `false` |
| `SEFCNET_JWT_SECRET` | JWT secret key | **REQUIRED** |
| `CORS_ORIGINS` | Allowed CORS origins | `*` |

### Security Configuration

**IMPORTANT**: Before deploying to production:

1. Generate a secure JWT secret:
   ```bash
   python -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

2. Set `SEFCNET_JWT_SECRET` in your `.env` file

3. Set `DEBUG=false` in production

4. Configure `CORS_ORIGINS` to specific domains

## Database Setup

SEFCNet uses SQLite by default (stored in `data/sefcnet.db`).

The database is automatically initialized on first startup.

### Migrating to PostgreSQL (Optional)

1. Install PostgreSQL dependencies:
   ```bash
   pip install asyncpg sqlalchemy
   ```

2. Update `DATABASE_URL` in `.env`:
   ```
   DATABASE_URL=postgresql+asyncpg://user:password@localhost/sefcnet
   ```

3. Update `auth/database.py` to use SQLAlchemy with asyncpg

## API Endpoints

### Authentication
- `POST /api/v1/auth/register` - Register new user
- `POST /api/v1/auth/login` - Login and get tokens
- `POST /api/v1/auth/refresh` - Refresh access token
- `POST /api/v1/auth/logout` - Logout and blacklist token

### System Management
- `GET /api/v1/system/state` - Get system state
- `POST /api/v1/system/services` - Deploy service

### Analytics
- `POST /api/v1/analytics/models` - Register model
- `POST /api/v1/analytics/experiments` - Create experiment

### Monitoring
- `GET /api/v1/monitoring/metrics` - Get metrics
- `GET /api/v1/monitoring/health` - Health check
- `GET /api/v1/monitoring/alerts/active` - Get active alerts

### Orchestration
- `POST /api/v1/orchestration/nodes` - Register node
- `POST /api/v1/orchestration/tasks` - Submit task

## Creating Your First User

### Using the API:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@sefcnet.com",
    "password": "SecurePassword123!",
    "roles": ["admin"],
    "permissions": ["ADMIN", "MANAGE", "WRITE", "READ"]
  }'
```

### Login:

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@sefcnet.com",
    "password": "SecurePassword123!"
  }'
```

Save the `access_token` from the response for authenticated requests.

## Docker Deployment

### Build Image:
```bash
docker build -t sefcnet:latest .
```

### Run Container:
```bash
docker run -d \
  --name sefcnet \
  -p 8000:8000 \
  -p 8501:8501 \
  -v $(pwd)/data:/app/data \
  -v $(pwd)/logs:/app/logs \
  --env-file .env \
  sefcnet:latest
```

## Kubernetes Deployment

See `infra/k8s/` directory for Kubernetes manifests.

```bash
kubectl apply -f infra/k8s/
```

## Monitoring

### Prometheus
- URL: http://localhost:9090
- Metrics endpoint: http://localhost:8000/api/v1/monitoring/metrics?format=prometheus

### Grafana
- URL: http://localhost:3000
- Default credentials: admin/admin

## Troubleshooting

### Database Issues
- Ensure `data/` directory exists and is writable
- Check database file permissions: `chmod 664 data/sefcnet.db`

### Port Conflicts
- Change `PORT` in `.env` if 8000 is already in use
- Update docker-compose.yml port mappings

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Check Python version: `python --version` (requires 3.11+)

### Authentication Issues
- Verify `SEFCNET_JWT_SECRET` is set
- Check token expiration settings in `.env`

## Production Checklist

- [ ] Set secure `SEFCNET_JWT_SECRET`
- [ ] Set `DEBUG=false`
- [ ] Configure `CORS_ORIGINS` properly
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set up monitoring and alerts
- [ ] Enable HTTPS/TLS
- [ ] Set up reverse proxy (nginx/traefik)
- [ ] Configure firewall rules
- [ ] Set up automated backups
- [ ] Review and test disaster recovery

## Support

For issues and questions:
- Check logs: `docker-compose logs sefcnet-api`
- Review API docs: http://localhost:8000/docs
- Check health: http://localhost:8000/health

