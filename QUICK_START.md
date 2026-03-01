# Quick Start Guide - Rizwan Universal AI

## ⚡ Get Running in 5 Minutes

For experienced developers who want to get started quickly.

---

## Prerequisites

- Python 3.11+
- Git
- A text editor

---

## Installation

```bash
# Clone project
git clone <repository-url>
cd rizwan-universal-ai

# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Initialize database
python -c "from database import init_db; init_db()"

# Start backend
python main.py
```

Backend runs on: **http://localhost:8000**

```bash
# Frontend setup (in new terminal)
cd frontend
python -m http.server 3000
```

Frontend runs on: **http://localhost:3000**

---

## Configuration

Create `.env` file in `backend/` directory:

```env
SECRET_KEY=<generate-with: python -c "import secrets; print(secrets.token_urlsafe(32))">
OPENAI_API_KEY=<your-openai-api-key>  # Optional
DATABASE_URL=sqlite:///./rizwan_ai.db
```

---

## API Endpoints

### Authentication
- `POST /api/auth/register` - Register user
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user
- `POST /api/auth/logout` - Logout

### Files
- `POST /api/files/upload` - Upload file
- `GET /api/files` - List files
- `DELETE /api/files/{id}` - Delete file

### AI Operations
- `POST /api/ai/generate` - Generate text
- `POST /api/ai/summarize` - Summarize text
- `POST /api/ai/answer` - Answer question
- `POST /api/ai/sentiment` - Analyze sentiment
- `POST /api/ai/code` - Generate code

### Health
- `GET /api/health` - Server health
- `GET /api/health/detailed` - Detailed health

---

## Project Structure

```
rizwan-universal-ai/
├── backend/                    # FastAPI application
│   ├── main.py                # Entry point
│   ├── database.py            # Models & DB config
│   ├── auth.py                # Authentication
│   ├── ai_service.py          # AI integration
│   ├── requirements.txt       # Dependencies
│   └── routes/                # API endpoints
│       ├── auth.py
│       ├── files.py
│       ├── ai.py
│       └── health.py
│
├── frontend/                   # HTML/CSS/JS application
│   ├── index.html             # Main page
│   ├── css/
│   │   ├── style.css
│   │   └── responsive.css
│   └── js/
│       ├── api.js
│       ├── auth.js
│       ├── ui.js
│       └── main.js
│
├── README.md                   # Project overview
├── SETUP.md                    # Detailed setup guide
├── API_REFERENCE.md            # API documentation
├── CODE_EXPLANATION.md         # Code walkthrough
├── DEPLOYMENT.md               # Production deployment
└── QUICK_START.md              # This file
```

---

## Common Tasks

### Test the Application

1. Open http://localhost:3000
2. Click "Sign Up"
3. Register with test credentials
4. Login
5. Try "Text Generation" feature

### Check API Documentation

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Stop Servers

- Backend: Press `Ctrl+C` in backend terminal
- Frontend: Press `Ctrl+C` in frontend terminal

### Restart Servers

```bash
# Backend
python main.py

# Frontend (new terminal)
python -m http.server 3000
```

---

## Key Files Explained

| File | Purpose |
|------|---------|
| `main.py` | FastAPI application entry point |
| `database.py` | Database models and configuration |
| `auth.py` | Password hashing and JWT tokens |
| `ai_service.py` | OpenAI API integration |
| `routes/` | API endpoint handlers |
| `index.html` | Main HTML page |
| `css/style.css` | Main stylesheet |
| `js/api.js` | API client |
| `js/auth.js` | Authentication UI |
| `js/ui.js` | UI interactions |
| `js/main.js` | Initialization |

---

## Troubleshooting

### "ModuleNotFoundError"
```bash
pip install -r requirements.txt
```

### "Port already in use"
```bash
# Find process using port 8000
lsof -i :8000
# Kill process
kill -9 <PID>
```

### "Database error"
```bash
# Reinitialize database
rm rizwan_ai.db
python -c "from database import init_db; init_db()"
```

### "AI requests fail"
1. Set `OPENAI_API_KEY` in .env
2. Get key from https://platform.openai.com/api-keys
3. Restart backend

---

## Next Steps

1. **Explore the Code**
   - Read CODE_EXPLANATION.md
   - Review each Python file
   - Understand the architecture

2. **Customize**
   - Change colors in `css/style.css`
   - Add new AI features in `routes/ai.py`
   - Extend database models

3. **Deploy**
   - Follow DEPLOYMENT.md
   - Choose hosting platform
   - Set up production database

4. **Learn More**
   - FastAPI docs: https://fastapi.tiangolo.com/
   - SQLAlchemy docs: https://docs.sqlalchemy.org/
   - JavaScript MDN: https://developer.mozilla.org/

---

## File Locations

**Backend:** `/home/ubuntu/rizwan-universal-ai/backend/`  
**Frontend:** `/home/ubuntu/rizwan-universal-ai/frontend/`  
**Documentation:** `/home/ubuntu/rizwan-universal-ai/`

---

## API Examples

### Register User
```bash
curl -X POST http://localhost:8000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "TestPass123",
    "full_name": "Test User"
  }'
```

### Login
```bash
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "TestPass123"
  }'
```

### Generate Text
```bash
curl -X POST http://localhost:8000/api/ai/generate \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Write a poem about AI",
    "max_tokens": 500,
    "temperature": 0.7
  }'
```

---

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `SECRET_KEY` | Required | JWT secret key |
| `DATABASE_URL` | sqlite:///./rizwan_ai.db | Database connection |
| `OPENAI_API_KEY` | Optional | OpenAI API key |
| `ENVIRONMENT` | development | Environment type |
| `DEBUG` | True | Debug mode |
| `LOG_LEVEL` | INFO | Logging level |

---

## Performance Tips

1. **Database:** Use PostgreSQL for production (not SQLite)
2. **Caching:** Implement Redis for frequently accessed data
3. **CDN:** Use CloudFront or Cloudflare for static files
4. **Monitoring:** Set up error tracking with Sentry
5. **Scaling:** Use load balancer for multiple servers

---

## Security Checklist

- [ ] Change `SECRET_KEY` to strong random value
- [ ] Set `DEBUG=False` in production
- [ ] Use HTTPS (SSL/TLS)
- [ ] Configure CORS for your domain only
- [ ] Use strong database passwords
- [ ] Keep dependencies updated
- [ ] Implement rate limiting
- [ ] Set up monitoring and logging

---

## Support

- **README.md** - Project overview
- **SETUP.md** - Detailed setup guide
- **API_REFERENCE.md** - API documentation
- **CODE_EXPLANATION.md** - Code walkthrough
- **DEPLOYMENT.md** - Production deployment

---

**Version:** 1.0.0  
**Last Updated:** January 2024  
**Created by:** Manus AI

---

## What's Next?

1. ✅ You have a working full-stack application
2. 📖 Read the documentation to understand the code
3. 🔧 Customize it for your needs
4. 🚀 Deploy to production
5. 📈 Scale and improve

**Happy Coding! 🎉**
