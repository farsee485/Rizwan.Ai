# Complete Setup Guide - Rizwan Universal AI

## 🎯 For Beginners: Step-by-Step Installation

This guide walks you through setting up the entire application from scratch. Even if you're new to programming, follow these steps carefully.

---

## Part 1: Prerequisites Installation

### Step 1.1: Install Python

**Windows:**
1. Visit https://www.python.org/downloads/
2. Download Python 3.11 or higher
3. Run the installer
4. **IMPORTANT:** Check "Add Python to PATH" during installation
5. Click "Install Now"
6. Verify installation:
   ```bash
   python --version
   ```

**macOS:**
```bash
# Using Homebrew (recommended)
brew install python@3.11

# Verify
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3-pip

# Verify
python3 --version
```

### Step 1.2: Install Git

**Windows:**
1. Download from https://git-scm.com/
2. Run installer with default settings
3. Verify: `git --version`

**macOS:**
```bash
brew install git
git --version
```

**Linux:**
```bash
sudo apt-get install git
git --version
```

### Step 1.3: Install a Code Editor

**Recommended: Visual Studio Code**
1. Download from https://code.visualstudio.com/
2. Install following default options
3. Install Python extension from VS Code marketplace

---

## Part 2: Project Setup

### Step 2.1: Download/Clone Project

**Option A: Using Git (Recommended)**
```bash
# Navigate to where you want the project
cd ~/Documents

# Clone the repository
git clone <repository-url>

# Navigate into project
cd rizwan-universal-ai
```

**Option B: Download ZIP**
1. Download the ZIP file from the repository
2. Extract it to a folder (e.g., `~/Documents/rizwan-universal-ai`)
3. Open terminal/command prompt in that folder

### Step 2.2: Verify Project Structure

```bash
# List the contents
ls -la

# You should see:
# - backend/
# - frontend/
# - README.md
# - SETUP.md
```

---

## Part 3: Backend Setup

### Step 3.1: Navigate to Backend

```bash
cd backend
```

### Step 3.2: Create Virtual Environment

A virtual environment isolates project dependencies from your system Python.

**Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**What you should see:**
```
(venv) $ _
```

The `(venv)` prefix indicates the virtual environment is active.

### Step 3.3: Install Dependencies

```bash
# Upgrade pip first
pip install --upgrade pip

# Install all required packages
pip install -r requirements.txt
```

This installs:
- FastAPI (web framework)
- Uvicorn (server)
- SQLAlchemy (database ORM)
- Pydantic (data validation)
- PyJWT (authentication)
- Bcrypt (password hashing)
- OpenAI (AI integration)
- And more...

**Installation time:** 2-5 minutes

### Step 3.4: Configure Environment

```bash
# Copy example configuration
cp CONFIG.md .env

# Edit .env file with your text editor
# On Windows: notepad .env
# On macOS/Linux: nano .env
```

**Important settings to update:**

```env
# Generate a secret key
SECRET_KEY=your-generated-key-here

# Optional: Add OpenAI API key (get from https://platform.openai.com/api-keys)
OPENAI_API_KEY=sk-your-api-key-here

# Database (SQLite is fine for development)
DATABASE_URL=sqlite:///./rizwan_ai.db
```

**Generate SECRET_KEY:**
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

Copy the output and paste it as the SECRET_KEY value.

### Step 3.5: Initialize Database

```bash
# Create database and tables
python -c "from database import init_db; init_db()"

# You should see:
# Database initialized successfully!
```

### Step 3.6: Test Backend

```bash
# Start the server
python main.py

# You should see:
# INFO:     Uvicorn running on http://0.0.0.0:8000
# INFO:     Application startup complete
```

**Keep this terminal open!**

### Step 3.7: Verify Backend is Running

Open your browser and visit:
- http://localhost:8000/docs (Swagger UI)
- http://localhost:8000/health (Health check)

You should see the API documentation.

---

## Part 4: Frontend Setup

### Step 4.1: Open New Terminal

Open a new terminal/command prompt window (keep backend running in the first one).

### Step 4.2: Navigate to Frontend

```bash
# From project root
cd frontend
```

### Step 4.3: Start Frontend Server

**Option A: Using Python (Recommended for Windows)**
```bash
python -m http.server 3000
```

**Option B: Using Node.js (if installed)**
```bash
npx http-server -p 3000
```

**Option C: Direct Browser**
Simply open `frontend/index.html` in your web browser.

### Step 4.4: Access the Application

Open your browser and visit:
```
http://localhost:3000
```

You should see the Rizwan Universal AI homepage!

---

## Part 5: Testing the Application

### Step 5.1: Register a New User

1. Click "Sign Up" button
2. Fill in the registration form:
   - Username: `testuser`
   - Email: `test@example.com`
   - Password: `TestPassword123`
   - Full Name: `Test User`
3. Click "Register"
4. You should see a success message

### Step 5.2: Login

1. Click "Login" button
2. Enter credentials:
   - Username: `testuser`
   - Password: `TestPassword123`
3. Click "Login"
4. You should be redirected to the dashboard

### Step 5.3: Test AI Features

1. In the dashboard, select "Text Generation"
2. Enter a prompt: "Write a short poem about AI"
3. Click "Generate"
4. Wait for the AI response

**Note:** If you haven't set OPENAI_API_KEY, you'll see a mock response.

### Step 5.4: Test File Upload

1. Select "Files" tab
2. Click the upload area or drag files
3. Upload a file (PDF, TXT, etc.)
4. File should appear in the list

---

## Part 6: Understanding the Code Structure

### Backend Organization

```
backend/
├── main.py              # Application entry point
├── database.py          # Database models & configuration
├── auth.py              # Authentication logic
├── ai_service.py        # AI integration
├── requirements.txt     # Python dependencies
└── routes/              # API endpoints
    ├── auth.py         # Login/Register endpoints
    ├── files.py        # File upload endpoints
    ├── ai.py           # AI operation endpoints
    └── health.py       # Health check endpoints
```

### Frontend Organization

```
frontend/
├── index.html           # Main HTML file
├── css/                 # Stylesheets
│   ├── style.css       # Main styles
│   └── responsive.css  # Mobile responsive
└── js/                  # JavaScript files
    ├── api.js          # API client
    ├── auth.js         # Authentication UI
    ├── ui.js           # UI interactions
    └── main.js         # Initialization
```

---

## Part 7: Common Tasks

### Stopping the Servers

**Backend:**
- Press `Ctrl+C` in the backend terminal

**Frontend:**
- Press `Ctrl+C` in the frontend terminal

### Restarting the Servers

```bash
# Backend (from backend directory with venv activated)
python main.py

# Frontend (from frontend directory)
python -m http.server 3000
```

### Deactivating Virtual Environment

```bash
deactivate
```

### Reactivating Virtual Environment

```bash
# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

---

## Part 8: Troubleshooting

### "Python is not recognized"

**Windows Solution:**
1. Uninstall Python
2. Reinstall and **CHECK "Add Python to PATH"**
3. Restart computer
4. Try again

### "ModuleNotFoundError: No module named 'fastapi'"

**Solution:**
```bash
# Make sure virtual environment is activated
# Then reinstall dependencies
pip install -r requirements.txt
```

### "Port 8000 already in use"

**Windows:**
```bash
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

**macOS/Linux:**
```bash
lsof -i :8000
kill -9 <PID>
```

### "Cannot connect to backend from frontend"

**Check:**
1. Backend is running (`python main.py`)
2. Frontend is accessing `http://localhost:8000/api`
3. CORS is enabled in backend
4. No firewall blocking port 8000

### "AI requests fail"

**Solution:**
1. Set OPENAI_API_KEY in .env file
2. Get API key from https://platform.openai.com/api-keys
3. Restart backend server

### "Database errors"

**Solution:**
```bash
# Delete old database
rm rizwan_ai.db

# Reinitialize
python -c "from database import init_db; init_db()"
```

---

## Part 9: Next Steps

### Learning Resources

1. **FastAPI Tutorial:** https://fastapi.tiangolo.com/tutorial/
2. **Python Guide:** https://docs.python.org/3/
3. **JavaScript MDN:** https://developer.mozilla.org/en-US/docs/Web/JavaScript/
4. **SQL Basics:** https://www.w3schools.com/sql/

### Customization Ideas

1. **Change Colors:** Edit `frontend/css/style.css`
2. **Add Features:** Create new endpoints in `backend/routes/`
3. **Modify Database:** Update models in `backend/database.py`
4. **Add Pages:** Create new HTML sections in `frontend/index.html`

### Deployment

See `DEPLOYMENT.md` for production deployment guides.

---

## Part 10: File Descriptions

### Backend Files

**main.py**
- Initializes FastAPI application
- Configures CORS, middleware, and routes
- Starts the server

**database.py**
- Defines database models (User, FileUpload, AISession)
- Manages database connections
- Provides query helpers

**auth.py**
- Handles password hashing
- Creates and validates JWT tokens
- Manages authentication logic

**ai_service.py**
- Interfaces with OpenAI API
- Provides text generation, summarization, etc.
- Includes mock service for testing

**routes/auth.py**
- User registration endpoint
- Login endpoint
- Token refresh endpoint

**routes/files.py**
- File upload endpoint
- File listing endpoint
- File deletion endpoint

**routes/ai.py**
- Text generation endpoint
- Summarization endpoint
- Sentiment analysis endpoint
- Code generation endpoint

**routes/health.py**
- Server health check
- Database health check
- AI service health check

### Frontend Files

**index.html**
- Main page structure
- Navigation bar
- Dashboard interface
- Authentication modals

**css/style.css**
- All styling for the application
- CSS variables for theming
- Component styles

**css/responsive.css**
- Mobile responsive design
- Tablet and desktop layouts
- Media queries

**js/api.js**
- API client for backend communication
- All API methods
- Token management

**js/auth.js**
- Login/Register form handlers
- Modal management
- Authentication UI updates

**js/ui.js**
- Tab switching
- Form submissions
- File upload handling
- Result display

**js/main.js**
- Application initialization
- Event listeners
- Global functionality

---

## Summary

You now have a complete, working full-stack application! Here's what you've set up:

✅ Backend API server (FastAPI)  
✅ Frontend web application (HTML/CSS/JavaScript)  
✅ Database (SQLite)  
✅ User authentication  
✅ File management  
✅ AI integration  

**Next:** Explore the code, make changes, and build on top of this foundation!

---

**Need Help?**
- Check the README.md for overview
- See API_REFERENCE.md for API details
- Review DEPLOYMENT.md for production setup
- Check troubleshooting section above

**Happy Coding! 🚀**
