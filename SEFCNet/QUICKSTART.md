# SEFCNet Quick Start Guide

Get SEFCNet up and running in 5 minutes!

## Prerequisites

- Python 3.11+ or Docker
- Git (to clone if needed)

## 🚀 Fastest Start (Docker)

```bash
# 1. Configure environment
cp .env.example .env

# 2. Generate JWT secret (IMPORTANT!)
python -c "import secrets; print('SEFCNET_JWT_SECRET=' + secrets.token_urlsafe(32))" >> .env

# 3. Start everything
docker-compose up -d

# 4. Check it's running
curl http://localhost:8000/health
```

**That's it!** Your API is now running at:
- **API**: http://localhost:8000
- **Docs**: http://localhost:8000/docs
- **Dashboard**: http://localhost:8501

## 📝 Create Your First User

```bash
curl -X POST "http://localhost:8000/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePass123!",
    "roles": ["admin"],
    "permissions": ["ADMIN", "MANAGE", "WRITE", "READ"]
  }'
```

## 🔑 Login

```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@example.com",
    "password": "SecurePass123!"
  }'
```

Save the `access_token` from the response!

## 🧪 Test Authenticated Endpoint

```bash
# Replace YOUR_TOKEN with the access_token from login
curl -X GET "http://localhost:8000/api/v1/system/state" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🛑 Stop Services

```bash
docker-compose down
```

## 📚 Next Steps

- Read [DEPLOYMENT.md](DEPLOYMENT.md) for production deployment
- Explore the API at http://localhost:8000/docs
- Check [README.md](README.md) for full feature list

## ❓ Troubleshooting

**Port already in use?**
- Change `PORT=8000` to another port in `.env`
- Update docker-compose.yml port mapping

**Database errors?**
- Ensure `data/` directory exists: `mkdir -p data`
- Check permissions: `chmod 755 data`

**Import errors?**
- Install dependencies: `pip install -r requirements.txt`
- Check Python version: `python --version` (needs 3.11+)

## 🎉 You're Ready!

Your SEFCNet MVP is now operational and ready for development!

