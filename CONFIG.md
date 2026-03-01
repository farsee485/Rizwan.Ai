# Rizwan Universal AI Backend - Configuration Guide

## Environment Variables

This document describes all environment variables needed to run the backend server.

### Server Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `SERVER_HOST` | `0.0.0.0` | Server host address |
| `SERVER_PORT` | `8000` | Server port |
| `ENVIRONMENT` | `development` | Environment: development, staging, production |
| `DEBUG` | `True` | Enable debug mode (set False in production) |

### Database Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `sqlite:///./rizwan_ai.db` | Database connection URL |

**Database URL Examples:**

- **SQLite** (development): `sqlite:///./rizwan_ai.db`
- **MySQL**: `mysql+pymysql://user:password@localhost:3306/rizwan_ai`
- **PostgreSQL**: `postgresql://user:password@localhost:5432/rizwan_ai`

### Authentication & Security

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | Required | Secret key for JWT encoding (generate with: `python -c "import secrets; print(secrets.token_urlsafe(32))"`) |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `30` | Access token expiration time |
| `REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Refresh token expiration time |

### AI/LLM Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `OPENAI_API_KEY` | Optional | OpenAI API key (get from https://platform.openai.com/api-keys) |
| `AI_MODEL` | `gpt-3.5-turbo` | AI model to use |

### File Upload Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `UPLOAD_DIR` | `./uploads` | Directory to store uploaded files |
| `MAX_FILE_SIZE` | `10485760` | Maximum file size in bytes (10 MB) |
| `ALLOWED_EXTENSIONS` | See below | Allowed file extensions |

**Allowed Extensions:** `pdf`, `txt`, `doc`, `docx`, `xls`, `xlsx`, `jpg`, `jpeg`, `png`, `gif`, `bmp`, `mp3`, `wav`, `mp4`, `avi`

### CORS Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `FRONTEND_URL` | `http://localhost:3000` | Frontend URL for CORS |
| `ALLOWED_ORIGINS` | `http://localhost:3000,http://localhost:8000` | Comma-separated allowed origins |

### Logging Configuration

| Variable | Default | Description |
|----------|---------|-------------|
| `LOG_LEVEL` | `INFO` | Log level: DEBUG, INFO, WARNING, ERROR, CRITICAL |
| `LOG_FILE` | `./logs/app.log` | Log file path |

## Setup Instructions

### 1. Create Environment File

```bash
# Copy the example environment file
cp backend/.env.example backend/.env

# Edit the .env file with your configuration
nano backend/.env
```

### 2. Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste it into `SECRET_KEY` in your `.env` file.

### 3. Set Up Database

For SQLite (development):
```bash
# No setup needed, database will be created automatically
```

For MySQL:
```bash
# Create database
mysql -u root -p
> CREATE DATABASE rizwan_ai;
> EXIT;

# Update DATABASE_URL in .env:
# DATABASE_URL=mysql+pymysql://root:password@localhost:3306/rizwan_ai
```

For PostgreSQL:
```bash
# Create database
createdb rizwan_ai

# Update DATABASE_URL in .env:
# DATABASE_URL=postgresql://user:password@localhost:5432/rizwan_ai
```

### 4. Install Python Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 5. Initialize Database

```bash
python -c "from database import init_db; init_db()"
```

### 6. Run the Server

```bash
# Development with auto-reload
python main.py

# Or using uvicorn directly
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

The server will be available at `http://localhost:8000`

- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## Production Deployment

### Security Checklist

- [ ] Change `SECRET_KEY` to a strong random value
- [ ] Set `DEBUG=False`
- [ ] Set `ENVIRONMENT=production`
- [ ] Use PostgreSQL or MySQL instead of SQLite
- [ ] Set `ALLOWED_ORIGINS` to your frontend domain only
- [ ] Use HTTPS (SSL/TLS certificate)
- [ ] Set up proper logging and monitoring
- [ ] Configure database backups
- [ ] Set up rate limiting
- [ ] Enable CORS only for trusted domains

### Environment Variables for Production

```bash
# Security
DEBUG=False
ENVIRONMENT=production
SECRET_KEY=<strong-random-key>

# Database (use managed database service)
DATABASE_URL=postgresql://user:password@db-host:5432/rizwan_ai

# AI
OPENAI_API_KEY=<your-api-key>

# CORS
ALLOWED_ORIGINS=https://yourdomain.com

# Logging
LOG_LEVEL=WARNING
```

### Deployment Platforms

#### Heroku

```bash
# Create Procfile
echo "web: uvicorn main:app --host 0.0.0.0 --port \$PORT" > Procfile

# Deploy
git push heroku main
```

#### Docker

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### AWS Lambda

Use AWS Lambda with API Gateway or use a containerized approach with ECS.

#### Google Cloud Run

```bash
gcloud run deploy rizwan-ai \
  --source . \
  --platform managed \
  --region us-central1 \
  --set-env-vars DATABASE_URL=<your-db-url>
```

## Troubleshooting

### Database Connection Error

**Problem:** `sqlalchemy.exc.OperationalError`

**Solution:**
1. Check `DATABASE_URL` in `.env`
2. Verify database server is running
3. Check database credentials
4. For MySQL: Install `mysql-connector-python` or `pymysql`
5. For PostgreSQL: Install `psycopg2-binary`

### AI Service Not Available

**Problem:** "AI service is not available"

**Solution:**
1. Check `OPENAI_API_KEY` is set in `.env`
2. Verify API key is valid at https://platform.openai.com/api-keys
3. Check API rate limits
4. Verify network connectivity

### File Upload Fails

**Problem:** "Failed to save file"

**Solution:**
1. Check `UPLOAD_DIR` directory exists and is writable
2. Verify file size doesn't exceed `MAX_FILE_SIZE`
3. Check file extension is in `ALLOWED_EXTENSIONS`
4. Verify disk space is available

### CORS Errors

**Problem:** "Access to XMLHttpRequest blocked by CORS policy"

**Solution:**
1. Add frontend URL to `ALLOWED_ORIGINS` in `.env`
2. Restart the server
3. Clear browser cache
4. Check browser console for specific error

## Additional Resources

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [JWT Authentication](https://tools.ietf.org/html/rfc7519)
