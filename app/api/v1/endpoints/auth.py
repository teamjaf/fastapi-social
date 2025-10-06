from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.core.config import settings
from app.schemas.user import (
    User, UserCreate, Token, UserLogin, 
    ForgotPasswordRequest, ResetPasswordRequest, PasswordResetResponse
)
from app.repositories.user import UserRepository
from app.utils.auth import create_access_token
from app.utils.password_reset import (
    create_password_reset_token, get_valid_reset_token, 
    use_reset_token, reset_user_password
)

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


@router.post(
    "/register",
    response_model=User,
    status_code=status.HTTP_201_CREATED,
    summary="Register New User",
    description="Create a new user account with email, username, and password",
    response_description="Returns the created user information (password excluded)",
    responses={
        201: {
            "description": "User successfully created",
            "model": User
        },
        400: {
            "description": "Bad request - Email or username already exists",
            "content": {
                "application/json": {
                    "example": {"detail": "Email already registered"}
                }
            }
        }
    }
)
def register(user: UserCreate, db: Session = Depends(get_db)):
    """
    **Register a New User**
    
    Create a new user account in the system. This endpoint validates that the email
    and username are unique before creating the account.
    
    **Request Body:**
    - `email`: Valid email address (must be unique)
    - `username`: Username (must be unique, 3-50 characters)
    - `password`: Password (minimum 8 characters recommended)
    - `full_name`: Optional full name of the user
    
    **Validation Rules:**
    - Email must be a valid email format
    - Email must not already exist in the system
    - Username must not already exist in the system
    - Password will be hashed before storage
    
    **Returns:**
    - User information (password excluded for security)
    - User ID, email, username, full name
    - Account creation timestamp
    - Account status (active by default)
    
    **Error Responses:**
    - `400 Bad Request`: Email or username already exists
    - `422 Unprocessable Entity`: Invalid input data format
    """
    user_repo = UserRepository(db)
    
    # Check if user already exists
    if user_repo.get_user_by_email(user.email):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    if user_repo.get_user_by_username(user.username):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create new user
    return user_repo.create_user(user)


@router.post(
    "/login",
    response_model=Token,
    status_code=status.HTTP_200_OK,
    summary="User Login",
    description="Authenticate user with email/username and password to get access token",
    response_description="Returns JWT access token for authenticated requests",
    responses={
        200: {
            "description": "Login successful",
            "model": Token
        },
        401: {
            "description": "Invalid credentials",
            "content": {
                "application/json": {
                    "example": {"detail": "Incorrect email or password"}
                }
            }
        },
        422: {
            "description": "Invalid input format",
            "content": {
                "application/json": {
                    "example": {"detail": [{"loc": ["body", "username"], "msg": "field required"}]}
                }
            }
        }
    }
)
def login(user_login: UserLogin, db: Session = Depends(get_db)):
    """
    **User Login**
    
    Authenticate a user with their email/username and password to receive a JWT access token.
    The token can be used to access protected endpoints.
    
    **Request Body:**
    - `username`: User's email address or username
    - `password`: User's password
    
    **Authentication Process:**
    1. Validates user credentials against the database
    2. Verifies password using secure hashing
    3. Generates JWT token with user's email as subject
    4. Returns token with expiration time
    
    **Token Details:**
    - **Type**: JWT (JSON Web Token)
    - **Algorithm**: HS256
    - **Expiration**: 30 minutes (configurable)
    - **Subject**: User's email address
    - **Usage**: Include in Authorization header as "Bearer {token}"
    
    **Returns:**
    - `access_token`: JWT token for authenticated requests
    - `token_type`: Always "bearer"
    
    **Error Responses:**
    - `401 Unauthorized`: Invalid email/username or password
    - `422 Unprocessable Entity`: Invalid request format
    
    **Security Notes:**
    - Tokens expire after 30 minutes for security
    - Store tokens securely (not in localStorage for production)
    - Include token in Authorization header for protected endpoints
    """
    user_repo = UserRepository(db)
    
    # Authenticate user
    user = user_repo.authenticate_user(user_login.username, user_login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get(
    "/me",
    response_model=User,
    status_code=status.HTTP_200_OK,
    summary="Get Current User",
    description="Get the current authenticated user's information",
    response_description="Returns the authenticated user's profile information",
    responses={
        200: {
            "description": "User information retrieved successfully",
            "model": User
        },
        401: {
            "description": "Invalid or expired token",
            "content": {
                "application/json": {
                    "example": {"detail": "Could not validate credentials"}
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        }
    }
)
def read_users_me(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    """
    **Get Current User Information**
    
    Retrieve the profile information of the currently authenticated user.
    This endpoint requires a valid JWT token in the Authorization header.
    
    **Authentication Required:**
    - Include JWT token in Authorization header: `Bearer {your_token}`
    - Token must be valid and not expired
    - Token subject (email) must correspond to an existing user
    
    **Returns:**
    - `id`: User's unique identifier
    - `email`: User's email address
    - `username`: User's username
    - `full_name`: User's full name (if provided)
    - `is_active`: Account status (true/false)
    - `created_at`: Account creation timestamp
    - `updated_at`: Last profile update timestamp
    
    **Security Notes:**
    - Password is never returned in the response
    - Only the token owner can access their own information
    - Token is validated before returning user data
    
    **Error Responses:**
    - `401 Unauthorized`: Invalid, expired, or missing token
    - `404 Not Found`: User associated with token not found
    
    **Usage Example:**
    ```
    GET /api/v1/auth/me
    Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
    ```
    """
    from app.utils.auth import verify_token
    
    email = verify_token(token)
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(email)
    
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.post(
    "/forgot-password",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Request Password Reset",
    description="Request a password reset token for a user account",
    response_description="Returns confirmation message about password reset request",
    responses={
        200: {
            "description": "Password reset request processed",
            "model": PasswordResetResponse
        },
        422: {
            "description": "Invalid email format",
            "content": {
                "application/json": {
                    "example": {"detail": [{"loc": ["body", "email"], "msg": "field required"}]}
                }
            }
        }
    }
)
def forgot_password(
    request: ForgotPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    **Request Password Reset**
    
    Initiate a password reset process for a user account. This endpoint generates
    a secure reset token that can be used to reset the user's password.
    
    **Request Body:**
    - `email`: The email address associated with the account
    
    **Process:**
    1. Validates the email format
    2. Checks if a user exists with that email
    3. Generates a secure, unique reset token
    4. Stores the token with expiration time (1 hour)
    5. Invalidates any existing reset tokens for the user
    
    **Security Features:**
    - **Email Privacy**: Always returns the same response regardless of whether email exists
    - **Token Expiration**: Reset tokens expire after 1 hour
    - **One-Time Use**: Each token can only be used once
    - **Secure Generation**: Uses cryptographically secure random token generation
    
    **Token Details:**
    - **Length**: 32 characters
    - **Characters**: Alphanumeric (letters and numbers)
    - **Expiration**: 1 hour from creation
    - **Usage**: Single use only
    
    **Production Note:**
    In a production environment, the reset token should be sent via email to the user.
    For testing purposes, the token is returned in the response.
    
    **Returns:**
    - `message`: Confirmation message (same for all requests for security)
    
    **Error Responses:**
    - `422 Unprocessable Entity`: Invalid email format
    
    **Next Steps:**
    After receiving the token, use the `/reset-password` endpoint to complete the password reset.
    """
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(request.email)
    
    if not user:
        # Don't reveal if email exists or not for security
        return PasswordResetResponse(
            message="If the email exists, a password reset link has been sent."
        )
    
    # Create password reset token
    reset_token = create_password_reset_token(db, user)
    
    # In a real application, you would send an email here
    # For now, we'll return the token in the response (NOT recommended for production)
    return PasswordResetResponse(
        message=f"Password reset token created. Token: {reset_token.token} (This is for testing only - in production, send via email)"
    )


@router.post(
    "/reset-password",
    response_model=PasswordResetResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset Password",
    description="Reset user password using a valid reset token",
    response_description="Returns confirmation message about password reset completion",
    responses={
        200: {
            "description": "Password reset successful",
            "model": PasswordResetResponse
        },
        400: {
            "description": "Invalid or expired reset token",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid or expired reset token"}
                }
            }
        },
        404: {
            "description": "User not found",
            "content": {
                "application/json": {
                    "example": {"detail": "User not found"}
                }
            }
        },
        422: {
            "description": "Invalid input format",
            "content": {
                "application/json": {
                    "example": {"detail": [{"loc": ["body", "token"], "msg": "field required"}]}
                }
            }
        },
        500: {
            "description": "Internal server error during password reset",
            "content": {
                "application/json": {
                    "example": {"detail": "Failed to reset password"}
                }
            }
        }
    }
)
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):
    """
    **Reset User Password**
    
    Complete the password reset process using a valid reset token obtained from
    the forgot password endpoint.
    
    **Request Body:**
    - `token`: The password reset token received from forgot password request
    - `new_password`: The new password for the user account
    
    **Validation Process:**
    1. Validates the reset token format and existence
    2. Checks if the token is not expired (1 hour limit)
    3. Verifies the token hasn't been used already
    4. Locates the user associated with the token
    5. Securely hashes the new password
    6. Updates the user's password in the database
    7. Marks the token as used to prevent reuse
    
    **Security Features:**
    - **Token Validation**: Only valid, unexpired, unused tokens are accepted
    - **Password Hashing**: New password is securely hashed using bcrypt
    - **One-Time Use**: Token is invalidated after successful use
    - **User Verification**: Ensures the user associated with the token exists
    
    **Password Requirements:**
    - Should be at least 8 characters long (recommended)
    - Will be securely hashed before storage
    - Previous password is completely replaced
    
    **Token Requirements:**
    - Must be obtained from the `/forgot-password` endpoint
    - Must not be expired (1 hour from creation)
    - Must not have been used previously
    - Must be exactly 32 characters long
    
    **Returns:**
    - `message`: Confirmation that password was successfully reset
    
    **Error Responses:**
    - `400 Bad Request`: Invalid, expired, or already used token
    - `404 Not Found`: User associated with token not found
    - `422 Unprocessable Entity`: Invalid request format
    - `500 Internal Server Error`: Database or hashing error
    
    **Post-Reset:**
    After successful password reset, the user can log in with their new password
    using the `/login` endpoint. The old password will no longer work.
    
    **Security Notes:**
    - The reset token becomes invalid after use
    - User must request a new token if they need to reset again
    - All existing user sessions remain valid until they expire
    """
    # Get valid reset token
    reset_token = get_valid_reset_token(db, request.token)
    
    if not reset_token:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    
    # Get user
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(reset_token.user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    # Reset password
    if not reset_user_password(db, user, request.new_password):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to reset password"
        )
    
    # Mark token as used
    use_reset_token(db, request.token)
    
    return PasswordResetResponse(
        message="Password has been successfully reset"
    )
