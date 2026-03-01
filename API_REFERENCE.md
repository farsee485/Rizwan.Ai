# API Reference - Rizwan Universal AI

## 📚 Complete API Documentation

This document provides detailed information about all API endpoints, request/response formats, and usage examples.

---

## Base URL

```
http://localhost:8000/api
```

For production, replace with your deployed server URL.

---

## Authentication

All protected endpoints require a JWT token in the Authorization header:

```http
Authorization: Bearer <access_token>
```

### Getting a Token

1. Register a new user at `/auth/register`
2. Login at `/auth/login` to receive `access_token`
3. Include the token in all subsequent requests

---

## Error Responses

All errors follow this format:

```json
{
  "detail": "Error message describing what went wrong"
}
```

### Common HTTP Status Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Created |
| 400 | Bad Request (invalid data) |
| 401 | Unauthorized (invalid/missing token) |
| 403 | Forbidden (insufficient permissions) |
| 404 | Not Found |
| 500 | Server Error |

---

## Authentication Endpoints

### 1. Register User

Creates a new user account.

```http
POST /auth/register
Content-Type: application/json

{
  "username": "johndoe",
  "email": "john@example.com",
  "password": "SecurePass123!",
  "full_name": "John Doe"
}
```

**Response (201 Created):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z"
}
```

**Validation Rules:**
- Username: 3-50 characters, alphanumeric
- Email: Valid email format
- Password: Minimum 8 characters
- Full Name: Optional, max 100 characters

---

### 2. Login User

Authenticates user and returns tokens.

```http
POST /auth/login
Content-Type: application/json

{
  "username": "johndoe",
  "password": "SecurePass123!"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

**Token Details:**
- `access_token`: Use for API requests (30 minutes validity)
- `refresh_token`: Use to get new access token (7 days validity)
- `expires_in`: Seconds until token expiration

---

### 3. Get Current User

Retrieves information about the authenticated user.

```http
GET /auth/me
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z",
  "last_signed_in": "2024-01-15T14:45:00Z"
}
```

---

### 4. Refresh Token

Gets a new access token using refresh token.

```http
POST /auth/refresh
Content-Type: application/json

{
  "refresh_token": "<refresh_token>"
}
```

**Response (200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

---

### 5. Logout

Invalidates the current session.

```http
POST /auth/logout
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Logged out successfully"
}
```

---

## User Endpoints

### 1. Get User Profile

Retrieves the authenticated user's profile.

```http
GET /users/profile
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "full_name": "John Doe",
  "created_at": "2024-01-15T10:30:00Z"
}
```

---

### 2. Update User Profile

Updates the authenticated user's profile information.

```http
PUT /users/profile
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "full_name": "John Smith",
  "email": "john.smith@example.com"
}
```

**Response (200 OK):**
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john.smith@example.com",
  "full_name": "John Smith",
  "updated_at": "2024-01-15T15:00:00Z"
}
```

---

### 3. Delete User Account

Permanently deletes the user account and all associated data.

```http
DELETE /users/account
Authorization: Bearer <access_token>
```

**Response (200 OK):**
```json
{
  "message": "Account deleted successfully"
}
```

**Warning:** This action cannot be undone!

---

## File Endpoints

### 1. Upload File

Uploads a file to the server.

```http
POST /files/upload
Authorization: Bearer <access_token>
Content-Type: multipart/form-data

Body:
file: <binary file content>
```

**Response (201 Created):**
```json
{
  "id": 1,
  "filename": "document.pdf",
  "file_size": 2048576,
  "file_type": "application/pdf",
  "uploaded_at": "2024-01-15T15:30:00Z",
  "download_url": "http://localhost:8000/api/files/1/download"
}
```

**Constraints:**
- Max file size: 10 MB
- Allowed types: PDF, TXT, DOC, DOCX, XLS, XLSX, JPG, PNG, MP3, MP4, etc.

---

### 2. List User Files

Retrieves a paginated list of files uploaded by the user.

```http
GET /files?skip=0&limit=10
Authorization: Bearer <access_token>
```

**Query Parameters:**
- `skip`: Number of files to skip (default: 0)
- `limit`: Maximum files to return (default: 10, max: 100)

**Response (200 OK):**
```json
{
  "files": [
    {
      "id": 1,
      "filename": "document.pdf",
      "file_size": 2048576,
      "file_type": "application/pdf",
      "uploaded_at": "2024-01-15T15:30:00Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 10
}
```

---

### 3. Get File Info

Retrieves information about a specific file.

```http
GET /files/{file_id}
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `file_id`: ID of the file (integer)

**Response (200 OK):**
```json
{
  "id": 1,
  "filename": "document.pdf",
  "file_size": 2048576,
  "file_type": "application/pdf",
  "uploaded_at": "2024-01-15T15:30:00Z",
  "download_url": "http://localhost:8000/api/files/1/download"
}
```

---

### 4. Delete File

Deletes a file from the server.

```http
DELETE /files/{file_id}
Authorization: Bearer <access_token>
```

**Path Parameters:**
- `file_id`: ID of the file (integer)

**Response (200 OK):**
```json
{
  "message": "File deleted successfully"
}
```

---

## AI Endpoints

### 1. Generate Text

Generates text using AI based on a prompt.

```http
POST /ai/generate
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "prompt": "Write a poem about artificial intelligence",
  "max_tokens": 500,
  "temperature": 0.7,
  "session_name": "Poetry Writing"
}
```

**Request Parameters:**
- `prompt` (required): The text prompt
- `max_tokens` (optional): Maximum tokens in response (default: 500, max: 2000)
- `temperature` (optional): Creativity level 0-1 (default: 0.7)
  - 0: Deterministic, focused
  - 1: Creative, random
- `session_name` (optional): Name for tracking this session

**Response (200 OK):**
```json
{
  "result": "In circuits deep and networks wide...",
  "tokens_used": 87,
  "model": "gpt-3.5-turbo",
  "session_id": "sess_123456"
}
```

---

### 2. Summarize Text

Summarizes a given text to a specified length.

```http
POST /ai/summarize
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "text": "Long article or document text here...",
  "max_length": 150,
  "session_name": "Article Summary"
}
```

**Request Parameters:**
- `text` (required): Text to summarize
- `max_length` (optional): Maximum summary length in characters (default: 150)
- `session_name` (optional): Session name for tracking

**Response (200 OK):**
```json
{
  "result": "This article discusses...",
  "original_length": 5000,
  "summary_length": 145,
  "compression_ratio": 0.029,
  "session_id": "sess_123456"
}
```

---

### 3. Answer Question

Answers a question based on provided context.

```http
POST /ai/answer
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "context": "Python is a high-level programming language...",
  "question": "What is Python used for?",
  "session_name": "Q&A Session"
}
```

**Request Parameters:**
- `context` (required): Background information
- `question` (required): Question to answer
- `session_name` (optional): Session name

**Response (200 OK):**
```json
{
  "result": "Python is used for web development, data analysis...",
  "confidence": 0.95,
  "session_id": "sess_123456"
}
```

---

### 4. Analyze Sentiment

Analyzes the sentiment of given text.

```http
POST /ai/sentiment
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "text": "I absolutely love this product! It's amazing!",
  "session_name": "Sentiment Analysis"
}
```

**Request Parameters:**
- `text` (required): Text to analyze
- `session_name` (optional): Session name

**Response (200 OK):**
```json
{
  "sentiment": "positive",
  "score": 0.95,
  "explanation": "The text expresses strong positive sentiment with words like 'love' and 'amazing'.",
  "session_id": "sess_123456"
}
```

**Sentiment Values:**
- `positive`: 0.5 - 1.0
- `neutral`: 0.4 - 0.6
- `negative`: 0.0 - 0.5

---

### 5. Generate Code

Generates code based on description and programming language.

```http
POST /ai/code
Authorization: Bearer <access_token>
Content-Type: application/json

{
  "description": "Function to calculate factorial of a number",
  "language": "Python",
  "session_name": "Code Generation"
}
```

**Request Parameters:**
- `description` (required): What the code should do
- `language` (optional): Programming language (default: Python)
  - Supported: Python, JavaScript, Java, C++, SQL, Go, Rust, PHP
- `session_name` (optional): Session name

**Response (200 OK):**
```json
{
  "result": "def factorial(n):\n    if n <= 1:\n        return 1\n    return n * factorial(n-1)",
  "language": "Python",
  "lines_of_code": 4,
  "session_id": "sess_123456"
}
```

---

## Health Check Endpoints

### 1. Basic Health Check

Checks if the server is running.

```http
GET /health
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "timestamp": "2024-01-15T15:45:00Z"
}
```

---

### 2. Detailed Health Check

Checks health of all system components.

```http
GET /health/detailed
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "components": {
    "database": "ok",
    "ai_service": "ok",
    "file_storage": "ok"
  },
  "timestamp": "2024-01-15T15:45:00Z"
}
```

---

### 3. Database Health Check

Checks database connectivity.

```http
GET /health/db
```

**Response (200 OK):**
```json
{
  "status": "ok",
  "database": "sqlite",
  "connection_time_ms": 2,
  "timestamp": "2024-01-15T15:45:00Z"
}
```

---

## Usage Examples

### Example 1: Complete Authentication Flow

```javascript
// 1. Register
const registerResponse = await fetch('http://localhost:8000/api/auth/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'johndoe',
    email: 'john@example.com',
    password: 'SecurePass123!',
    full_name: 'John Doe'
  })
});

// 2. Login
const loginResponse = await fetch('http://localhost:8000/api/auth/login', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    username: 'johndoe',
    password: 'SecurePass123!'
  })
});

const { access_token } = await loginResponse.json();

// 3. Use token for protected requests
const userResponse = await fetch('http://localhost:8000/api/auth/me', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});
```

### Example 2: File Upload and Processing

```javascript
// 1. Create FormData
const formData = new FormData();
const fileInput = document.getElementById('fileInput');
formData.append('file', fileInput.files[0]);

// 2. Upload file
const uploadResponse = await fetch('http://localhost:8000/api/files/upload', {
  method: 'POST',
  headers: { 'Authorization': `Bearer ${access_token}` },
  body: formData
});

const fileData = await uploadResponse.json();
console.log('File uploaded:', fileData.filename);

// 3. List files
const listResponse = await fetch('http://localhost:8000/api/files?limit=10', {
  headers: { 'Authorization': `Bearer ${access_token}` }
});

const files = await listResponse.json();
console.log('Total files:', files.total);
```

### Example 3: AI Text Generation

```javascript
// Generate text with AI
const aiResponse = await fetch('http://localhost:8000/api/ai/generate', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${access_token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    prompt: 'Write a haiku about programming',
    max_tokens: 100,
    temperature: 0.8,
    session_name: 'Creative Writing'
  })
});

const result = await aiResponse.json();
console.log('Generated text:', result.result);
console.log('Tokens used:', result.tokens_used);
```

---

## Rate Limiting

Currently, there are no rate limits. In production, implement:
- 100 requests per minute per user
- 1000 requests per hour per IP
- 10 concurrent requests per user

---

## Pagination

List endpoints support pagination:

```http
GET /files?skip=0&limit=10
```

- `skip`: Offset (default: 0)
- `limit`: Page size (default: 10, max: 100)

---

## Versioning

Current API version: **v1**

Future versions will be available at:
```
/api/v2/...
```

---

## Support

For API issues:
1. Check error response for details
2. Review this documentation
3. Check server logs
4. Verify authentication token is valid

---

**Last Updated:** January 2024  
**API Version:** 1.0.0
