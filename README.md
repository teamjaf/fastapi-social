# 🚀 Fast Social Media API

<div align="center">

![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Python](https://img.shields.io/badge/python-3670A0?style=for-the-badge&logo=python&logoColor=ffdd54)
![PostgreSQL](https://img.shields.io/badge/postgresql-%23316192.svg?style=for-the-badge&logo=postgresql&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-1C4E80?style=for-the-badge&logo=sqlalchemy&logoColor=white)

**A modern, clean architecture FastAPI-based social media application for university students**

[Features](#-features) • [Quick Start](#-quick-start) • [API Documentation](#-api-documentation) • [Profile Fields](#-profile-fields)

</div>

## 📁 Project Structure

```
app/
├── __init__.py
├── main.py                 # 🚀 FastAPI application entry point
├── api/                    # 🌐 API layer
│   └── v1/
│       ├── __init__.py
│       ├── router.py       # 🔗 API router configuration
│       └── endpoints/      # 📡 API endpoints
│           ├── __init__.py
│           ├── health.py   # ❤️ Health check endpoints
│           ├── auth.py     # 🔐 Authentication endpoints
│           └── profile.py  # 👤 User profile endpoints
├── core/                   # ⚙️ Core configuration
│   ├── __init__.py
│   ├── config.py          # 🔧 Application settings
│   └── database.py        # 🗄️ Database configuration
├── models/                 # 📊 Database models
│   ├── __init__.py
│   ├── user.py            # 👤 User model
│   └── password_reset.py  # 🔑 Password reset model
├── schemas/                # 📋 Pydantic schemas
│   ├── __init__.py
│   ├── user.py            # 👤 User schemas
│   └── profile.py         # 📝 Profile schemas
├── services/               # 🏢 Business logic layer
├── repositories/           # 💾 Data access layer
│   ├── __init__.py
│   └── user.py            # 👤 User repository
├── utils/                  # 🛠️ Utility functions
│   ├── __init__.py
│   ├── auth.py            # 🔐 Authentication utilities
│   └── password_reset.py  # 🔑 Password reset utilities
└── alembic/               # 🗃️ Database migrations
    ├── versions/
    └── env.py
```

## ✨ Features

- 🏗️ **Clean Architecture** - Separation of concerns with layered architecture
- 🔐 **JWT Authentication** - Secure token-based authentication system
- 👤 **User Management** - Registration, login, password reset functionality
- 📝 **Rich Profiles** - Comprehensive user profiles with academic and personal information
- 📝 **Posts & Feed** - Content sharing with posts, likes, comments, and personalized feed
- 🔍 **Advanced Search** - Filter and search users by multiple criteria
- 📄 **Pagination** - Efficient data retrieval with pagination support
- 🎯 **Gender & Religion** - Optional demographic fields for better user matching
- 🏫 **University Focus** - Designed specifically for university students
- 📚 **Auto Documentation** - Interactive Swagger UI documentation
- 🗄️ **PostgreSQL** - Robust database with SQLAlchemy ORM
- 🔄 **Database Migrations** - Alembic for schema versioning
- 🌐 **CORS Support** - Cross-origin resource sharing configuration
- ⚙️ **Environment Config** - Flexible configuration management

## 🚀 Quick Start

### 🎯 Option 1: Automated Setup (Recommended)

**Windows:**
```bash
setup_venv.bat
```

**Linux/Mac:**
```bash
chmod +x setup_venv.sh
./setup_venv.sh
```

### 🛠️ Option 2: Manual Setup

1. **Create virtual environment:**
```bash
python -m venv venv
```

2. **Activate virtual environment:**
```bash
# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

4. **Set up database:**
```bash
# Run database migrations
alembic upgrade head
```

## 🏃‍♂️ Running the Application

### 🚀 Production (with Gunicorn):
```bash
gunicorn app.main:app -c gunicorn.conf.py
```

### 🔧 Development (with Uvicorn):
```bash
uvicorn app.main:app --host 0.0.0.0 --port 9090 --reload
```

### 🌐 API Endpoints

The API will be available at:
- 🏠 **Main API**: http://localhost:9090
- ❤️ **Health Check**: http://localhost:9090/api/v1/health/
- 📄 **OpenAPI Schema**: http://localhost:9090/api/v1/openapi.json
- 📚 **Interactive Docs**: http://localhost:9090/docs

## 📚 API Documentation

### ❤️ Health Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/api/v1/health/` | Basic health check |
| `GET` | `/api/v1/health/ready` | Readiness check |

### 🔐 Authentication Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/auth/register` | Register a new user | ❌ |
| `POST` | `/api/v1/auth/login` | Login user and get access token | ❌ |
| `GET` | `/api/v1/auth/me` | Get current user information | ✅ |
| `POST` | `/api/v1/auth/forgot-password` | Request password reset token | ❌ |
| `POST` | `/api/v1/auth/reset-password` | Reset password using token | ❌ |

### 👤 User Profile Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `GET` | `/api/v1/profile/me` | Get current user's complete profile | ✅ |
| `PUT` | `/api/v1/profile/me` | Update current user's profile | ✅ |
| `PATCH` | `/api/v1/profile/me` | Partially update profile fields | ✅ |
| `DELETE` | `/api/v1/profile/me` | Delete user account | ✅ |
| `GET` | `/api/v1/profile/all` | Get all user profiles with pagination and filtering | ❌ |
| `GET` | `/api/v1/profile/{user_id}` | Get public profile of any user | ❌ |
| `GET` | `/api/v1/profile/search` | Search profiles by criteria | ❌ |
| `POST` | `/api/v1/profile/me/verify-school-email` | Verify school email | ✅ |

### 📝 Posts & Feed Endpoints
| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|---------------|
| `POST` | `/api/v1/posts` | Create a new post | ✅ |
| `GET` | `/api/v1/posts/feed` | Get personalized feed from connections | ✅ |
| `GET` | `/api/v1/posts/{post_id}` | Get single post with details | ❌ |
| `PUT` | `/api/v1/posts/{post_id}` | Update own post | ✅ |
| `DELETE` | `/api/v1/posts/{post_id}` | Delete own post | ✅ |
| `GET` | `/api/v1/posts/user/{user_id}` | Get user's posts with privacy filtering | ❌ |
| `POST` | `/api/v1/posts/{post_id}/like` | Like/unlike post (toggle) | ✅ |
| `GET` | `/api/v1/posts/{post_id}/likes` | Get users who liked post | ❌ |
| `POST` | `/api/v1/posts/{post_id}/comments` | Add comment to post | ✅ |
| `GET` | `/api/v1/posts/{post_id}/comments` | Get post comments with replies | ❌ |
| `PUT` | `/api/v1/posts/comments/{comment_id}` | Update own comment | ✅ |
| `DELETE` | `/api/v1/posts/comments/{comment_id}` | Delete own comment | ✅ |

## 💡 Example Usage

### 🔐 Authentication Examples

**1. Register a new user:**
```bash
curl -X POST "http://localhost:9090/api/v1/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@university.edu",
    "username": "johndoe123",
    "password": "securepassword123",
    "full_name": "John Doe",
    "university": "Tech University"
  }'
```

**2. Login (with email or username):**
```bash
curl -X POST "http://localhost:9090/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john.doe@university.edu",
    "password": "securepassword123"
  }'
```

**3. Get user info (requires token):**
```bash
curl -X GET "http://localhost:9090/api/v1/auth/me" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**4. Forgot password:**
```bash
curl -X POST "http://localhost:9090/api/v1/auth/forgot-password" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john.doe@university.edu"
  }'
```

**5. Reset password:**
```bash
curl -X POST "http://localhost:9090/api/v1/auth/reset-password" \
  -H "Content-Type: application/json" \
  -d '{
    "token": "RESET_TOKEN_FROM_EMAIL",
    "new_password": "newpassword123"
  }'
```

### 👤 Profile Management Examples

**6. Update user profile:**
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

**7. Get all profiles with filtering:**
```bash
curl -X GET "http://localhost:9090/api/v1/profile/all?limit=10&offset=0&university=Tech%20University&gender=male"
```

**8. Search profiles:**
```bash
curl -X GET "http://localhost:9090/api/v1/profile/search?university=Tech%20University&major=Computer%20Science&limit=10"
```

### 📝 Posts & Feed Examples

**9. Create a new post:**
```bash
curl -X POST "http://localhost:9090/api/v1/posts" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Just finished my AI project! Excited to share the results with everyone.",
    "media_urls": ["https://example.com/project-image.jpg"],
    "privacy": "public"
  }'
```

**10. Get personalized feed:**
```bash
curl -X GET "http://localhost:9090/api/v1/posts/feed?limit=10&offset=0" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**11. Like a post:**
```bash
curl -X POST "http://localhost:9090/api/v1/posts/1/like" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**12. Add a comment:**
```bash
curl -X POST "http://localhost:9090/api/v1/posts/1/comments" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Amazing work! Would love to learn more about your approach."
  }'
```

**13. Get post comments:**
```bash
curl -X GET "http://localhost:9090/api/v1/posts/1/comments?limit=10&offset=0"
```

**14. Update your post:**
```bash
curl -X PUT "http://localhost:9090/api/v1/posts/1" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "content": "Updated: Just finished my AI project! Here are the final results.",
    "privacy": "connections"
  }'
```

## 📝 Profile Fields

The user profile system supports comprehensive fields for university students:

### 🎓 Academic Information
| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `university` | String | University name | ✅ |
| `campus` | String | Campus location | ❌ |
| `major` | String | Academic major | ❌ |
| `current_class` | Enum | Academic year (freshman, sophomore, junior, senior, graduate, phd, postdoc) | ❌ |
| `graduation_year` | Integer | Expected graduation year | ❌ |
| `enrollment_status` | Enum | Current status (enrolled, graduated, dropped_out, on_leave, transferred) | ❌ |
| `current_role` | Enum | Role (student, alumni, faculty, staff, visiting_scholar) | ❌ |

### 👤 Personal Information
| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `full_name` | String | Full name | ✅ |
| `email` | Email | Primary email address | ✅ |
| `username` | String | Unique username | ✅ |
| `school_email` | Email | University email address | ❌ |
| `is_school_email_verified` | Boolean | Email verification status | ❌ |
| `avatar_url` | String | Profile picture URL | ❌ |
| `dob` | Date | Date of birth | ❌ |
| `gender` | Enum | Gender (male, female) | ❌ |
| `religion` | Enum | Religion (islam, hindu, christian, other) | ❌ |

### 📖 Bio & Interests
| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `one_line_bio` | String | Short bio | ❌ |
| `full_bio` | Text | Detailed bio | ❌ |
| `hobbies` | Array | Array of hobbies | ❌ |
| `interests` | Array | Array of interests | ❌ |
| `dream_role` | String | Dream profession or role | ❌ |
| `links` | Array | Array of social links | ❌ |

### 💼 Professional
| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `current_organization` | String | Current organization/company | ❌ |

## ⚙️ Configuration

Environment variables can be set in a `.env` file:

| Variable | Description | Default |
|----------|-------------|---------|
| `PROJECT_NAME` | Project name | "Fast Social Media API" |
| `VERSION` | API version | "1.0.0" |
| `BACKEND_CORS_ORIGINS` | Comma-separated list of allowed CORS origins | "*" |
| `DATABASE_URL` | PostgreSQL database connection string | Required |
| `SECRET_KEY` | JWT secret key for token generation | Required |
| `ALGORITHM` | JWT algorithm | "HS256" |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token expiration time in minutes | 30 |

## 🛠️ Technology Stack

- **Backend Framework**: FastAPI
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Authentication**: JWT (JSON Web Tokens)
- **Password Hashing**: bcrypt
- **API Documentation**: Swagger UI / OpenAPI
- **Database Migrations**: Alembic
- **Production Server**: Gunicorn
- **Development Server**: Uvicorn

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add some amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- FastAPI for the amazing web framework
- SQLAlchemy for the ORM
- PostgreSQL for the robust database
- All contributors who help improve this project

---

<div align="center">

**Made with ❤️ for university students**

[⭐ Star this repo](https://github.com/your-repo/fast-social) • [🐛 Report Bug](https://github.com/your-repo/fast-social/issues) • [💡 Request Feature](https://github.com/your-repo/fast-social/issues)

</div>
