# Deployment Guide - Rizwan Universal AI

## 🚀 Production Deployment

This guide covers deploying the Rizwan Universal AI application to production environments.

---

## Pre-Deployment Checklist

Before deploying, ensure:

- [ ] All code is tested and working locally
- [ ] Environment variables are configured
- [ ] Database is set up on production server
- [ ] SSL/TLS certificate is obtained
- [ ] Domain name is registered and configured
- [ ] Backup strategy is in place
- [ ] Monitoring and logging are configured
- [ ] Security headers are set
- [ ] CORS is properly configured
- [ ] Rate limiting is implemented

---

## Security Hardening

### 1. Update Configuration

```env
# production.env
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=<generate-strong-key>
ALLOWED_ORIGINS=https://yourdomain.com
DATABASE_URL=postgresql://user:password@db-host:5432/rizwan_ai
OPENAI_API_KEY=<your-api-key>
LOG_LEVEL=WARNING
```

### 2. Generate Strong Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

### 3. Security Headers

Add to backend configuration:

```python
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

app.add_middleware(
    TrustedHostMiddleware,
    allowed_hosts=["yourdomain.com", "www.yourdomain.com"]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://yourdomain.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Deployment Options

### Option 1: Heroku (Easiest)

#### Prerequisites
- Heroku account (free tier available)
- Heroku CLI installed

#### Steps

```bash
# 1. Login to Heroku
heroku login

# 2. Create app
heroku create your-app-name

# 3. Add PostgreSQL
heroku addons:create heroku-postgresql:hobby-dev

# 4. Set environment variables
heroku config:set SECRET_KEY=<your-secret-key>
heroku config:set OPENAI_API_KEY=<your-api-key>
heroku config:set ENVIRONMENT=production

# 5. Create Procfile in backend directory
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > backend/Procfile

# 6. Deploy
git push heroku main

# 7. Initialize database
heroku run "python -c 'from database import init_db; init_db()'" -a your-app-name

# 8. View logs
heroku logs --tail
```

**Pros:** Easy setup, automatic scaling, free tier available  
**Cons:** Limited customization, can be expensive at scale

---

### Option 2: AWS (Scalable)

#### Using Elastic Beanstalk

```bash
# 1. Install EB CLI
pip install awsebcli

# 2. Initialize
eb init -p python-3.11 rizwan-ai --region us-east-1

# 3. Create environment
eb create production --instance-type t3.micro

# 4. Set environment variables
eb setenv SECRET_KEY=<your-secret-key> OPENAI_API_KEY=<your-api-key>

# 5. Deploy
eb deploy

# 6. View logs
eb logs

# 7. Open application
eb open
```

#### Using EC2

1. Launch EC2 instance (Ubuntu 22.04)
2. SSH into instance
3. Install dependencies:
   ```bash
   sudo apt-get update
   sudo apt-get install python3.11 python3.11-venv python3-pip nginx
   ```
4. Clone repository
5. Set up application (see SETUP.md)
6. Configure Nginx as reverse proxy
7. Use Gunicorn as application server
8. Set up SSL with Let's Encrypt

---

### Option 3: Google Cloud Run (Containerized)

#### Prerequisites
- Docker installed
- Google Cloud account

#### Steps

```bash
# 1. Create Dockerfile
cat > backend/Dockerfile << 'EOF'
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
EOF

# 2. Build image
docker build -t gcr.io/PROJECT_ID/rizwan-ai:latest backend/

# 3. Push to Google Container Registry
docker push gcr.io/PROJECT_ID/rizwan-ai:latest

# 4. Deploy to Cloud Run
gcloud run deploy rizwan-ai \
  --image gcr.io/PROJECT_ID/rizwan-ai:latest \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=<your-db-url>,SECRET_KEY=<key>
```

---

### Option 4: DigitalOcean (Affordable)

#### Using App Platform

1. Connect GitHub repository
2. Create new app
3. Configure environment variables
4. Deploy

#### Using Droplets

```bash
# 1. Create droplet (Ubuntu 22.04)
# 2. SSH into droplet
# 3. Install dependencies
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3-pip nginx certbot python3-certbot-nginx

# 4. Clone and set up application
# 5. Configure Nginx
# 6. Set up SSL
sudo certbot certonly --nginx -d yourdomain.com
```

---

## Database Setup

### PostgreSQL (Recommended for Production)

```bash
# 1. Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# 2. Create database
sudo -u postgres createdb rizwan_ai

# 3. Create user
sudo -u postgres createuser rizwan_user
sudo -u postgres psql -c "ALTER USER rizwan_user WITH PASSWORD 'secure_password';"

# 4. Grant privileges
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE rizwan_ai TO rizwan_user;"

# 5. Update DATABASE_URL
DATABASE_URL=postgresql://rizwan_user:secure_password@localhost:5432/rizwan_ai
```

### MySQL

```bash
# 1. Install MySQL
sudo apt-get install mysql-server

# 2. Create database
mysql -u root -p
> CREATE DATABASE rizwan_ai;
> CREATE USER 'rizwan_user'@'localhost' IDENTIFIED BY 'secure_password';
> GRANT ALL PRIVILEGES ON rizwan_ai.* TO 'rizwan_user'@'localhost';
> FLUSH PRIVILEGES;

# 3. Update DATABASE_URL
DATABASE_URL=mysql+pymysql://rizwan_user:secure_password@localhost:3306/rizwan_ai
```

---

## SSL/TLS Certificate

### Using Let's Encrypt

```bash
# 1. Install Certbot
sudo apt-get install certbot python3-certbot-nginx

# 2. Obtain certificate
sudo certbot certonly --standalone -d yourdomain.com -d www.yourdomain.com

# 3. Configure Nginx to use certificate
# See Nginx configuration below

# 4. Auto-renewal
sudo certbot renew --dry-run
```

---

## Nginx Configuration

Create `/etc/nginx/sites-available/rizwan-ai`:

```nginx
upstream backend {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "DENY" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # Frontend
    location / {
        root /var/www/rizwan-ai/frontend;
        try_files $uri $uri/ /index.html;
    }

    # Backend API
    location /api/ {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript;
}
```

Enable the site:

```bash
sudo ln -s /etc/nginx/sites-available/rizwan-ai /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

---

## Application Server (Gunicorn)

### Installation

```bash
pip install gunicorn
```

### Create systemd Service

Create `/etc/systemd/system/rizwan-ai.service`:

```ini
[Unit]
Description=Rizwan Universal AI
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/rizwan-ai/backend
Environment="PATH=/var/www/rizwan-ai/backend/venv/bin"
ExecStart=/var/www/rizwan-ai/backend/venv/bin/gunicorn \
    --workers 4 \
    --worker-class uvicorn.workers.UvicornWorker \
    --bind 127.0.0.1:8000 \
    main:app

[Install]
WantedBy=multi-user.target
```

Start service:

```bash
sudo systemctl daemon-reload
sudo systemctl start rizwan-ai
sudo systemctl enable rizwan-ai
```

---

## Monitoring & Logging

### Application Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/app.log'),
        logging.StreamHandler()
    ]
)
```

### System Monitoring

```bash
# Install monitoring tools
sudo apt-get install htop iotop nethogs

# Monitor application
htop

# View logs
tail -f /var/log/syslog
journalctl -u rizwan-ai -f
```

### Uptime Monitoring

Use services like:
- Uptime Robot (free)
- New Relic
- DataDog
- Sentry (error tracking)

---

## Backup Strategy

### Database Backup

```bash
# PostgreSQL
pg_dump -U rizwan_user rizwan_ai > backup_$(date +%Y%m%d).sql

# MySQL
mysqldump -u rizwan_user -p rizwan_ai > backup_$(date +%Y%m%d).sql
```

### Automated Backup

Create cron job:

```bash
# Edit crontab
crontab -e

# Add daily backup at 2 AM
0 2 * * * pg_dump -U rizwan_user rizwan_ai > /backups/backup_$(date +\%Y\%m\%d).sql
```

### Cloud Backup

Use AWS S3, Google Cloud Storage, or DigitalOcean Spaces for offsite backups.

---

## Performance Optimization

### Database Indexing

```python
# In database.py
class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
```

### Caching

```python
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

FastAPICache2.init(RedisBackend(url="redis://localhost"), prefix="fastapi-cache")
```

### CDN for Static Files

Use CloudFront, Cloudflare, or Bunny CDN for frontend assets.

---

## Scaling Strategies

### Horizontal Scaling

1. Load balancer (Nginx, HAProxy)
2. Multiple application servers
3. Shared database
4. Cache layer (Redis)

### Vertical Scaling

1. Increase server resources (CPU, RAM)
2. Optimize code and queries
3. Use connection pooling

---

## Troubleshooting

### Application Won't Start

```bash
# Check logs
journalctl -u rizwan-ai -n 50

# Check port
netstat -tlnp | grep 8000

# Check permissions
ls -la /var/www/rizwan-ai
```

### Database Connection Issues

```bash
# Test connection
psql -U rizwan_user -d rizwan_ai -h localhost

# Check connection string
echo $DATABASE_URL
```

### High Memory Usage

```bash
# Check process
ps aux | grep gunicorn

# Limit workers
gunicorn --workers 2 ...
```

---

## Post-Deployment

1. **Test all features** in production
2. **Monitor logs** for errors
3. **Set up alerts** for failures
4. **Document deployment** process
5. **Create runbook** for common issues
6. **Schedule maintenance** windows
7. **Plan disaster recovery**

---

## Rollback Procedure

```bash
# If deployment fails
git revert <commit-hash>
git push

# Redeploy
git push heroku main
# or
eb deploy
# or
docker push and redeploy
```

---

## Continuous Deployment

### GitHub Actions Example

```yaml
name: Deploy to Production

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Deploy to Heroku
        run: |
          git push https://heroku:${{ secrets.HEROKU_API_KEY }}@git.heroku.com/${{ secrets.HEROKU_APP_NAME }}.git main
```

---

## Support

For deployment issues:
1. Check logs
2. Review this guide
3. Check platform-specific documentation
4. Contact platform support

---

**Last Updated:** January 2024  
**Version:** 1.0.0
