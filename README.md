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
- `POST /api/v1/auth/forgot-password` - Request password reset token
- `POST /api/v1/auth/reset-password` - Reset password using token

### User Profile Endpoints
- `GET /api/v1/profile/me` - Get current user's complete profile (requires authentication)
- `PUT /api/v1/profile/me` - Update current user's profile (requires authentication)
- `PATCH /api/v1/profile/me` - Partially update profile fields (requires authentication)
- `DELETE /api/v1/profile/me` - Delete user account (requires authentication)
- `GET /api/v1/profile/all` - Get all user profiles with pagination and filtering
- `GET /api/v1/profile/{user_id}` - Get public profile of any user
- `GET /api/v1/profile/search` - Search profiles by criteria
- `POST /api/v1/profile/me/verify-school-email` - Verify school email (requires authentication)

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

**Forgot password:**
```bash
curl -X POST "http://localhost:9090/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com"
  }'
```

**Reset password:**
```bash
curl -X POST "http://localhost:9090/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "RESET_TOKEN_FROM_EMAIL",
    "new_password": "newpassword123"
  }'
```

**Update user profile:**
```bash
curl -X PUT "http://localhost:9090/api/v1/profile/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "university": "Tech University",
    "campus": "Main Campus",
    "major": "Computer Science",
    "current_class": "senior",
    "graduation_year": 2025,
    "current_role": "student",
    "one_line_bio": "CS student passionate about AI",
    "interests": ["Machine Learning", "Web Development"],
    "hobbies": ["Coding", "Reading", "Gaming"],
    "dream_role": "Senior Software Engineer at Google",
    "gender": "male",
    "religion": "islam"
  }'
```

**Search profiles:**
```bash
curl -X GET "http://localhost:9090/api/v1/profile/search?university=Tech%20University&major=Computer%20Science&limit=10"
```

## Profile Fields

The user profile system supports the following fields:

**Academic Information:**
- `university` - University name
- `campus` - Campus location
- `major` - Academic major
- `current_class` - Academic year (freshman, sophomore, junior, senior, graduate, phd, postdoc)
- `graduation_year` - Expected graduation year
- `enrollment_status` - Current status (enrolled, graduated, dropped_out, on_leave, transferred)
- `current_role` - Role (student, alumni, faculty, staff, visiting_scholar)

**Personal Information:**
- `full_name` - Full name
- `school_email` - University email address
- `is_school_email_verified` - Email verification status
- `avatar_url` - Profile picture URL
- `dob` - Date of birth
- `gender` - Gender (male, female)
- `religion` - Religion (islam, hindu, christian, other)

**Bio & Interests:**
- `one_line_bio` - Short bio
- `full_bio` - Detailed bio
- `hobbies` - Array of hobbies
- `interests` - Array of interests
- `dream_role` - Dream profession or role
- `links` - Array of social links

**Professional:**
- `current_organization` - Current organization/company

## Configuration

Environment variables can be set in a `.env` file:
- `PROJECT_NAME`: Project name (default: "Fast Social Media API")
- `VERSION`: API version (default: "1.0.0")
- `BACKEND_CORS_ORIGINS`: Comma-separated list of allowed CORS origins
