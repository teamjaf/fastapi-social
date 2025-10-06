# Fast Social Media API

A clean architecture FastAPI-based social media application.

## Project Structure

```
app/
├── __init__.py
├── main.py                 # FastAPI application entry point
├── api/                    # API layer
│   └── v1/
│       ├── __init__.py
│       ├── router.py       # API router configuration
│       └── endpoints/      # API endpoints
│           ├── __init__.py
│           └── health.py   # Health check endpoints
├── core/                   # Core configuration
│   ├── __init__.py
│   └── config.py          # Application settings
├── models/                 # Database models
├── schemas/                # Pydantic schemas
├── services/               # Business logic layer
├── repositories/           # Data access layer
└── utils/                  # Utility functions
```

## Features

- Clean architecture separation of concerns
- Health check endpoints
- CORS middleware configuration
- Environment-based configuration
- FastAPI with automatic OpenAPI documentation

## Setup

### Option 1: Automated Setup (Recommended)

**Windows:**
```bash
setup_venv.bat
```

**Linux/Mac:**
```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

### Option 2: Manual Setup

1. Create virtual environment:
```bash
python -m venv venv
```

2. Activate virtual environment:
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. Install dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## Running the Application

### Production (with Gunicorn):
```bash
gunicorn app.main:app -c gunicorn.conf.py
```

### Development (with Uvicorn):
```bash
uvicorn app.main:app --host 0.0.0.0 --port 9090 --reload
```

The API will be available at:
- Main API: http://localhost:9090
- Health check: http://localhost:9090/api/v1/health/
- API documentation: http://localhost:9090/api/v1/openapi.json
- Interactive docs: http://localhost:9090/docs

## API Endpoints

### Health Endpoints
- `GET /api/v1/health/` - Basic health check
- `GET /api/v1/health/ready` - Readiness check

### Authentication Endpoints
- `POST /api/v1/auth/register` - Register a new user
- `POST /api/v1/auth/login` - Login user and get access token
- `GET /api/v1/auth/me` - Get current user information (requires authentication)

### Example Usage

**Register a new user:**
```bash
curl -X POST "http://localhost:9090/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "username": "username",
    "password": "password123",
    "full_name": "Full Name"
  }'
```

**Login:**
```bash
curl -X POST "http://localhost:9090/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "user@example.com",
    "password": "password123"
  }'
```

**Get user info (requires token):**
```bash
curl -X GET "http://localhost:9090/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

## Configuration

Environment variables can be set in a `.env` file:
- `PROJECT_NAME`: Project name (default: "Fast Social Media API")
- `VERSION`: API version (default: "1.0.0")
- `BACKEND_CORS_ORIGINS`: Comma-separated list of allowed CORS origins
