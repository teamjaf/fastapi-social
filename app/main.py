from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.api.v1.router import api_router
from app.core.config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Social Media API",
    openapi_url=f"{settings.API_V1_STR}/openapi.json"
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Include API router
app.include_router(api_router, prefix=settings.API_V1_STR)

# Custom documentation page
@app.get("/", response_class=HTMLResponse, include_in_schema=False)
async def custom_docs():
    """Custom beautiful documentation page for the Fast Social Media API"""
    return HTMLResponse(content="""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Fast Social Media API - Documentation</title>
    <link rel="stylesheet" href="/static/css/docs.css">
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap" rel="stylesheet">
</head>
<body>
    <div class="container">
        <header class="header">
            <h1>Fast Social Media API</h1>
            <p>A modern, fast, and secure social media API built with FastAPI</p>
            <span class="version-badge">Version 1.0.0</span>
        </header>

        <div class="nav-section">
            <h2 style="color: var(--primary-color); margin-bottom: 1rem; font-size: 1.5rem; font-weight: 700;">Quick Navigation</h2>
            <div class="nav-grid">
                <a href="#health" class="nav-item">
                    <h3>🏥 Health Check</h3>
                    <p>Monitor API status and readiness</p>
                </a>
                <a href="#auth" class="nav-item">
                    <h3>🔐 Authentication</h3>
                    <p>User registration, login, and password management</p>
                </a>
                <a href="#profile" class="nav-item">
                    <h3>👤 User Profiles</h3>
                    <p>Profile management and user information</p>
                </a>
                <a href="#connections" class="nav-item">
                    <h3>🤝 Connections</h3>
                    <p>Social connections and friend management</p>
                </a>
                <a href="#posts" class="nav-item">
                    <h3>📝 Posts & Feed</h3>
                    <p>Content sharing, likes, comments, and personalized feed</p>
                </a>
            </div>
        </div>

        <div class="quick-links">
            <h2>Quick Links</h2>
            <div class="links-grid">
                <a href="/docs" class="quick-link">Interactive API Docs</a>
                <a href="/redoc" class="quick-link">ReDoc Documentation</a>
                <a href="/api/v1/openapi.json" class="quick-link">OpenAPI Schema</a>
                <a href="/api/v1/health/" class="quick-link">Health Check</a>
            </div>
        </div>

        <div class="card" id="health">
            <div class="card-header">
                <h2>🏥 Health Check Endpoints</h2>
                <p>Monitor the API status and ensure everything is running smoothly</p>
            </div>
            <div class="card-body">
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/health/</span>
                    </div>
                    <div class="endpoint-description">
                        Check if the API is running and healthy. Returns current status, timestamp, and message.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> API is healthy</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Use Cases</h4>
                            <ul>
                                <li>Monitoring and alerting systems</li>
                                <li>Load balancer health checks</li>
                                <li>Basic connectivity testing</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/health/ready</span>
                    </div>
                    <div class="endpoint-description">
                        Check if the API is ready to serve requests. More comprehensive than basic health check.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> API is ready</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Use Cases</h4>
                            <ul>
                                <li>Kubernetes readiness probes</li>
                                <li>Service mesh health checks</li>
                                <li>Pre-deployment verification</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card" id="auth">
            <div class="card-header">
                <h2>🔐 Authentication Endpoints</h2>
                <p>Complete user authentication system with JWT tokens and password management</p>
            </div>
            <div class="card-body">
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-post">POST</span>
                        <span class="endpoint-path">/api/v1/auth/register</span>
                    </div>
                    <div class="endpoint-description">
                        Create a new user account with email, username, password, full_name, and university.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-201">201</span> User created successfully</li>
                                <li><span class="status-code status-400">400</span> Email or username already exists</li>
                                <li><span class="status-code status-422">422</span> Invalid input format</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Required Fields</h4>
                            <ul>
                                <li>email (unique)</li>
                                <li>username (unique, 3-50 chars)</li>
                                <li>password (min 8 chars)</li>
                                <li>full_name</li>
                                <li>university</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-post">POST</span>
                        <span class="endpoint-path">/api/v1/auth/login</span>
                    </div>
                    <div class="endpoint-description">
                        Authenticate user with email/username and password to get JWT access token.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Login successful</li>
                                <li><span class="status-code status-401">401</span> Invalid credentials</li>
                                <li><span class="status-code status-422">422</span> Invalid input format</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Token Details</h4>
                            <ul>
                                <li>Type: JWT (HS256)</li>
                                <li>Expiration: 30 minutes</li>
                                <li>Usage: Bearer token in Authorization header</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/auth/me</span>
                    </div>
                    <div class="endpoint-description">
                        Get current authenticated user's information. Requires valid JWT token.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> User info retrieved</li>
                                <li><span class="status-code status-401">401</span> Invalid/expired token</li>
                                <li><span class="status-code status-404">404</span> User not found</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Authentication</h4>
                            <ul>
                                <li>Bearer token required</li>
                                <li>Include in Authorization header</li>
                                <li>Token must be valid and not expired</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-post">POST</span>
                        <span class="endpoint-path">/api/v1/auth/forgot-password</span>
                    </div>
                    <div class="endpoint-description">
                        Request a password reset token for a user account. Token expires in 1 hour.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Reset request processed</li>
                                <li><span class="status-code status-422">422</span> Invalid email format</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Security Features</h4>
                            <ul>
                                <li>Email privacy protection</li>
                                <li>1-hour token expiration</li>
                                <li>One-time use tokens</li>
                                <li>Secure token generation</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-post">POST</span>
                        <span class="endpoint-path">/api/v1/auth/reset-password</span>
                    </div>
                    <div class="endpoint-description">
                        Reset user password using a valid reset token from forgot-password endpoint.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Password reset successful</li>
                                <li><span class="status-code status-400">400</span> Invalid/expired token</li>
                                <li><span class="status-code status-404">404</span> User not found</li>
                                <li><span class="status-code status-500">500</span> Server error</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Required Fields</h4>
                            <ul>
                                <li>token (from forgot-password)</li>
                                <li>new_password (min 8 chars)</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card" id="profile">
            <div class="card-header">
                <h2>👤 User Profile Endpoints</h2>
                <p>Comprehensive user profile management with search and filtering capabilities</p>
            </div>
            <div class="card-body">
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/profile/me</span>
                    </div>
                    <div class="endpoint-description">
                        Get current user's complete profile information including sensitive data.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Profile retrieved</li>
                                <li><span class="status-code status-401">401</span> Authentication required</li>
                                <li><span class="status-code status-404">404</span> User not found</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Includes</h4>
                            <ul>
                                <li>Complete profile data</li>
                                <li>Sensitive information (email, dob)</li>
                                <li>Only accessible by owner</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-put">PUT</span>
                        <span class="endpoint-path">/api/v1/profile/me</span>
                    </div>
                    <div class="endpoint-description">
                        Update current user's profile information. Only provided fields are updated.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Profile updated</li>
                                <li><span class="status-code status-400">400</span> No fields provided</li>
                                <li><span class="status-code status-401">401</span> Authentication required</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Validation Rules</h4>
                            <ul>
                                <li>graduation_year: 1900-2034</li>
                                <li>dob: Cannot be in future</li>
                                <li>school_email: Valid email format</li>
                                <li>links: Array of objects with 'url'</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/profile/all</span>
                    </div>
                    <div class="endpoint-description">
                        Get all user profiles with pagination and optional filtering.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Query Parameters</h4>
                            <ul>
                                <li>limit: 1-100 (default: 20)</li>
                                <li>offset: Skip count (default: 0)</li>
                                <li>university: Filter by university</li>
                                <li>major: Filter by major</li>
                                <li>current_role: Filter by role</li>
                                <li>gender: Filter by gender</li>
                                <li>religion: Filter by religion</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Profiles retrieved</li>
                                <li><span class="status-code status-422">422</span> Invalid parameters</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/profile/{user_id}</span>
                    </div>
                    <div class="endpoint-description">
                        Get a user's public profile information (sensitive data excluded).
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Profile retrieved</li>
                                <li><span class="status-code status-404">404</span> User not found</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Excluded Data</h4>
                            <ul>
                                <li>Email addresses</li>
                                <li>Date of birth</li>
                                <li>Private bio</li>
                                <li>Account status</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/profile/search</span>
                    </div>
                    <div class="endpoint-description">
                        Search for users based on various profile criteria with advanced filtering.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Search Parameters</h4>
                            <ul>
                                <li>university, campus, major</li>
                                <li>current_class, graduation_year</li>
                                <li>current_role, interests</li>
                                <li>limit, offset (pagination)</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Search Behavior</h4>
                            <ul>
                                <li>Case-insensitive partial matches</li>
                                <li>Multiple parameters with AND logic</li>
                                <li>Interest matching (any specified)</li>
                                <li>Only active users included</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-delete">DELETE</span>
                        <span class="endpoint-path">/api/v1/profile/me</span>
                    </div>
                    <div class="endpoint-description">
                        Permanently delete current user's account and all associated data.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-204">204</span> Account deleted</li>
                                <li><span class="status-code status-401">401</span> Authentication required</li>
                                <li><span class="status-code status-404">404</span> User not found</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Security Warning</h4>
                            <ul>
                                <li>Permanent action (cannot be undone)</li>
                                <li>All data deleted</li>
                                <li>Consider soft delete in production</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card" id="connections">
            <div class="card-header">
                <h2>🤝 Connection Management Endpoints</h2>
                <p>Complete social connection system with friend requests, blocking, and suggestions</p>
            </div>
            <div class="card-body">
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-post">POST</span>
                        <span class="endpoint-path">/api/v1/connections/request/{user_id}</span>
                    </div>
                    <div class="endpoint-description">
                        Send a connection request to another user. Cannot send to yourself or blocked users.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-201">201</span> Request sent</li>
                                <li><span class="status-code status-400">400</span> Invalid request</li>
                                <li><span class="status-code status-403">403</span> User blocked</li>
                                <li><span class="status-code status-404">404</span> User not found</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Validation</h4>
                            <ul>
                                <li>Cannot send to yourself</li>
                                <li>Cannot send to blocked users</li>
                                <li>No duplicate pending requests</li>
                                <li>Target user must be active</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-post">POST</span>
                        <span class="endpoint-path">/api/v1/connections/accept/{connection_id}</span>
                    </div>
                    <div class="endpoint-description">
                        Accept a pending connection request sent to you.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Request accepted</li>
                                <li><span class="status-code status-404">404</span> Request not found</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Permissions</h4>
                            <ul>
                                <li>Only request recipient can accept</li>
                                <li>Request must be pending</li>
                                <li>Connection becomes active</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-post">POST</span>
                        <span class="endpoint-path">/api/v1/connections/reject/{connection_id}</span>
                    </div>
                    <div class="endpoint-description">
                        Reject a pending connection request sent to you.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Request rejected</li>
                                <li><span class="status-code status-404">404</span> Request not found</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Permissions</h4>
                            <ul>
                                <li>Only request recipient can reject</li>
                                <li>Request must be pending</li>
                                <li>Connection marked as rejected</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/connections/my-connections</span>
                    </div>
                    <div class="endpoint-description">
                        Get all accepted connections (friends list) with pagination.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Query Parameters</h4>
                            <ul>
                                <li>limit: 1-100 (default: 20)</li>
                                <li>offset: Skip count (default: 0)</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Connections retrieved</li>
                                <li><span class="status-code status-401">401</span> Authentication required</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/connections/requests/received</span>
                    </div>
                    <div class="endpoint-description">
                        Get connection requests sent to you (pending requests).
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Query Parameters</h4>
                            <ul>
                                <li>limit: 1-100 (default: 20)</li>
                                <li>offset: Skip count (default: 0)</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Requests retrieved</li>
                                <li><span class="status-code status-401">401</span> Authentication required</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/connections/requests/sent</span>
                    </div>
                    <div class="endpoint-description">
                        Get connection requests you sent (pending requests).
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Query Parameters</h4>
                            <ul>
                                <li>limit: 1-100 (default: 20)</li>
                                <li>offset: Skip count (default: 0)</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Requests retrieved</li>
                                <li><span class="status-code status-401">401</span> Authentication required</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/connections/status/{user_id}</span>
                    </div>
                    <div class="endpoint-description">
                        Check connection status with a specific user.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Status retrieved</li>
                                <li><span class="status-code status-401">401</span> Authentication required</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Status Types</h4>
                            <ul>
                                <li>null: No connection</li>
                                <li>pending: Request pending</li>
                                <li>accepted: Connected</li>
                                <li>rejected: Request rejected</li>
                                <li>blocked: User blocked</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/connections/mutual/{user_id}</span>
                    </div>
                    <div class="endpoint-description">
                        Get mutual connections with another user.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Query Parameters</h4>
                            <ul>
                                <li>limit: 1-100 (default: 20)</li>
                                <li>offset: Skip count (default: 0)</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Mutual connections retrieved</li>
                                <li><span class="status-code status-404">404</span> User not found</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/connections/suggestions</span>
                    </div>
                    <div class="endpoint-description">
                        Get friend suggestions based on mutual connections, university, major, and interests.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Query Parameters</h4>
                            <ul>
                                <li>limit: 1-100 (default: 20)</li>
                                <li>offset: Skip count (default: 0)</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Suggestion Factors</h4>
                            <ul>
                                <li>Mutual connections count</li>
                                <li>Common university</li>
                                <li>Common major</li>
                                <li>Common interests</li>
                                <li>Suggestion score</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-post">POST</span>
                        <span class="endpoint-path">/api/v1/connections/block/{user_id}</span>
                    </div>
                    <div class="endpoint-description">
                        Block a user to prevent connection requests and interactions.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> User blocked</li>
                                <li><span class="status-code status-400">400</span> Cannot block yourself</li>
                                <li><span class="status-code status-404">404</span> User not found</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Block Effects</h4>
                            <ul>
                                <li>Prevents connection requests</li>
                                <li>Blocks all interactions</li>
                                <li>Cannot send requests to blocked user</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-delete">DELETE</span>
                        <span class="endpoint-path">/api/v1/connections/unblock/{user_id}</span>
                    </div>
                    <div class="endpoint-description">
                        Unblock a previously blocked user.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-204">204</span> User unblocked</li>
                                <li><span class="status-code status-404">404</span> User not blocked</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Unblock Effects</h4>
                            <ul>
                                <li>Removes block status</li>
                                <li>Allows connection requests</li>
                                <li>Restores normal interactions</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-delete">DELETE</span>
                        <span class="endpoint-path">/api/v1/connections/remove/{user_id}</span>
                    </div>
                    <div class="endpoint-description">
                        Remove an existing connection (unfriend).
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-204">204</span> Connection removed</li>
                                <li><span class="status-code status-404">404</span> Connection not found</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Remove Effects</h4>
                            <ul>
                                <li>Ends friendship/connection</li>
                                <li>Removes from friends list</li>
                                <li>Can reconnect later if desired</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/connections/stats</span>
                    </div>
                    <div class="endpoint-description">
                        Get connection statistics for current user.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Stats retrieved</li>
                                <li><span class="status-code status-401">401</span> Authentication required</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Statistics Included</h4>
                            <ul>
                                <li>Total connections</li>
                                <li>Pending requests received</li>
                                <li>Pending requests sent</li>
                                <li>Blocked users count</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>

        <div class="card" id="posts">
            <div class="card-header">
                <h2>📝 Posts & Feed Endpoints</h2>
                <p>Complete content sharing system with posts, likes, comments, and personalized feed</p>
            </div>
            <div class="card-body">
                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-post">POST</span>
                        <span class="endpoint-path">/api/v1/posts</span>
                    </div>
                    <div class="endpoint-description">
                        Create a new post with content, optional media URLs, and privacy settings.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Request Body</h4>
                            <ul>
                                <li>content: Post text (required, 1-5000 chars)</li>
                                <li>media_urls: Array of media URLs (optional, max 10)</li>
                                <li>privacy: public, connections, or private</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-201">201</span> Post created</li>
                                <li><span class="status-code status-401">401</span> Authentication required</li>
                                <li><span class="status-code status-422">422</span> Invalid input</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/posts/feed</span>
                    </div>
                    <div class="endpoint-description">
                        Get personalized feed with posts from your connections in chronological order.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Query Parameters</h4>
                            <ul>
                                <li>limit: 1-100 (default: 20)</li>
                                <li>offset: Skip count (default: 0)</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Feed Content</h4>
                            <ul>
                                <li>Posts from accepted connections</li>
                                <li>Your own posts</li>
                                <li>Public and connections-only posts</li>
                                <li>Ordered by creation date (newest first)</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/posts/{post_id}</span>
                    </div>
                    <div class="endpoint-description">
                        Get a single post by ID with author information and interaction counts.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Privacy Rules</h4>
                            <ul>
                                <li>Public posts: Visible to everyone</li>
                                <li>Connections posts: Visible to accepted connections</li>
                                <li>Private posts: Visible only to author</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Post retrieved</li>
                                <li><span class="status-code status-403">403</span> Access denied</li>
                                <li><span class="status-code status-404">404</span> Post not found</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-put">PUT</span>
                        <span class="endpoint-path">/api/v1/posts/{post_id}</span>
                    </div>
                    <div class="endpoint-description">
                        Update your own post's content, media URLs, or privacy settings.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Authorization</h4>
                            <ul>
                                <li>Only post author can update</li>
                                <li>At least one field must be provided</li>
                                <li>Content validation applies</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Post updated</li>
                                <li><span class="status-code status-400">400</span> No fields provided</li>
                                <li><span class="status-code status-404">404</span> Post not found</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-delete">DELETE</span>
                        <span class="endpoint-path">/api/v1/posts/{post_id}</span>
                    </div>
                    <div class="endpoint-description">
                        Delete your own post (soft delete preserves data integrity).
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Authorization</h4>
                            <ul>
                                <li>Only post author can delete</li>
                                <li>Soft delete preserves data</li>
                                <li>Post marked as inactive</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-204">204</span> Post deleted</li>
                                <li><span class="status-code status-404">404</span> Post not found</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-post">POST</span>
                        <span class="endpoint-path">/api/v1/posts/{post_id}/like</span>
                    </div>
                    <div class="endpoint-description">
                        Toggle like status on a post (like/unlike functionality).
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Toggle Behavior</h4>
                            <ul>
                                <li>Like if not already liked</li>
                                <li>Unlike if already liked</li>
                                <li>Returns updated like count</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Like toggled</li>
                                <li><span class="status-code status-404">404</span> Post not found</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/posts/{post_id}/likes</span>
                    </div>
                    <div class="endpoint-description">
                        Get users who liked a specific post with pagination.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Query Parameters</h4>
                            <ul>
                                <li>limit: 1-100 (default: 20)</li>
                                <li>offset: Skip count (default: 0)</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Likes retrieved</li>
                                <li><span class="status-code status-404">404</span> Post not found</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-post">POST</span>
                        <span class="endpoint-path">/api/v1/posts/{post_id}/comments</span>
                    </div>
                    <div class="endpoint-description">
                        Add a comment to a post (top-level or reply to another comment).
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Request Body</h4>
                            <ul>
                                <li>content: Comment text (required, 1-1000 chars)</li>
                                <li>parent_comment_id: For replies (optional)</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Comment Types</h4>
                            <ul>
                                <li>Top-level: No parent_comment_id</li>
                                <li>Replies: Include parent_comment_id</li>
                                <li>Nested structure supported</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/posts/{post_id}/comments</span>
                    </div>
                    <div class="endpoint-description">
                        Get comments for a post with nested replies structure.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Comment Structure</h4>
                            <ul>
                                <li>Top-level comments first</li>
                                <li>Nested replies included</li>
                                <li>Ordered by creation date</li>
                                <li>Author information included</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Query Parameters</h4>
                            <ul>
                                <li>limit: 1-100 (default: 20)</li>
                                <li>offset: Skip count (default: 0)</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-put">PUT</span>
                        <span class="endpoint-path">/api/v1/posts/comments/{comment_id}</span>
                    </div>
                    <div class="endpoint-description">
                        Update your own comment content.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Authorization</h4>
                            <ul>
                                <li>Only comment author can update</li>
                                <li>Content validation applies</li>
                                <li>Updated timestamp</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-200">200</span> Comment updated</li>
                                <li><span class="status-code status-404">404</span> Comment not found</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-delete">DELETE</span>
                        <span class="endpoint-path">/api/v1/posts/comments/{comment_id}</span>
                    </div>
                    <div class="endpoint-description">
                        Delete your own comment (soft delete preserves data).
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Authorization</h4>
                            <ul>
                                <li>Only comment author can delete</li>
                                <li>Soft delete preserves data</li>
                                <li>Comment count updated</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Response Codes</h4>
                            <ul>
                                <li><span class="status-code status-204">204</span> Comment deleted</li>
                                <li><span class="status-code status-404">404</span> Comment not found</li>
                            </ul>
                        </div>
                    </div>
                </div>

                <div class="endpoint">
                    <div class="endpoint-header">
                        <span class="method-badge method-get">GET</span>
                        <span class="endpoint-path">/api/v1/posts/user/{user_id}</span>
                    </div>
                    <div class="endpoint-description">
                        Get posts from a specific user with privacy filtering.
                    </div>
                    <div class="endpoint-details">
                        <div class="detail-section">
                            <h4>Privacy Filtering</h4>
                            <ul>
                                <li>Public posts: Always visible</li>
                                <li>Connections posts: Visible to connections</li>
                                <li>Private posts: Visible only to author</li>
                            </ul>
                        </div>
                        <div class="detail-section">
                            <h4>Query Parameters</h4>
                            <ul>
                                <li>limit: 1-100 (default: 20)</li>
                                <li>offset: Skip count (default: 0)</li>
                            </ul>
                        </div>
                    </div>
                </div>
            </div>
        </div>

                <footer class="footer">
                    <p>Developed by Mohammad Jafrin | Fast Social Media API v1.0.0</p>
                    <p>For interactive API testing, visit <a href="/docs" style="color: rgba(255, 255, 255, 0.8);">/docs</a> or <a href="/redoc" style="color: rgba(255, 255, 255, 0.8);">/redoc</a></p>
                </footer>
    </div>

    <script src="/static/js/docs.js"></script>
</body>
</html>
    """)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9090)
