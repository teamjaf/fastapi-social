from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.profile import (
    ProfileCreate, ProfileUpdate, ProfileResponse, ProfilePublic, ProfileSearch
)
from app.repositories.user import UserRepository
from app.utils.auth import verify_token

router = APIRouter()
security = HTTPBearer()


def get_current_user_id(credentials: HTTPAuthorizationCredentials = Depends(security), db: Session = Depends(get_db)) -> int:
    """Get current user ID from JWT token"""
    email = verify_token(credentials.credentials)
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_email(email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    return user.id


@router.get(
    "/me",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Get My Profile",
    description="Get the current user's complete profile information",
    response_description="Returns the authenticated user's complete profile"
)
def get_my_profile(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    **Get My Profile**
    
    Retrieve the complete profile information of the currently authenticated user.
    This includes all profile fields including sensitive information like email and date of birth.
    
    **Authentication Required:**
    - Valid JWT token in Authorization header
    
    **Returns:**
    - Complete user profile with all fields
    - Sensitive information included (email, dob, etc.)
    - Only accessible by the profile owner
    """
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(current_user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.put(
    "/me",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Update My Profile",
    description="Update the current user's profile information",
    response_description="Returns the updated user profile"
)
def update_my_profile(
    profile_update: ProfileUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    **Update My Profile**
    
    Update the profile information of the currently authenticated user.
    Only provided fields will be updated; omitted fields remain unchanged.
    
    **Authentication Required:**
    - Valid JWT token in Authorization header
    
    **Request Body:**
    - Any combination of profile fields
    - Fields not provided will remain unchanged
    - Validation rules apply to provided fields
    
    **Validation Rules:**
    - `graduation_year`: Must be between 1900 and 2034
    - `dob`: Cannot be in the future
    - `links`: Must be array of objects with 'url' field
    - `school_email`: Must be valid email format
    
    **Returns:**
    - Updated user profile
    - All fields including updated ones
    """
    user_repo = UserRepository(db)
    
    # Get update data, excluding None values
    update_data = profile_update.dict(exclude_unset=True, exclude_none=True)
    
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )
    
    updated_user = user_repo.update_user_profile(current_user_id, update_data)
    
    if not updated_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return updated_user


@router.patch(
    "/me",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Partially Update My Profile",
    description="Partially update specific fields in the current user's profile",
    response_description="Returns the updated user profile"
)
def patch_my_profile(
    profile_update: ProfileUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    **Partially Update My Profile**
    
    Partially update specific fields in the user's profile. This is an alias for PUT /me
    but emphasizes that only provided fields will be updated.
    
    **Authentication Required:**
    - Valid JWT token in Authorization header
    
    **Request Body:**
    - Only include fields you want to update
    - Omitted fields remain unchanged
    - Can update single field or multiple fields
    
    **Example:**
    ```json
    {
        "major": "Computer Science",
        "graduation_year": 2025
    }
    ```
    
    **Returns:**
    - Updated user profile with all fields
    """
    return update_my_profile(profile_update, current_user_id, db)


@router.get(
    "/all",
    response_model=List[ProfilePublic],
    status_code=status.HTTP_200_OK,
    summary="Get All Profiles",
    description="Retrieve all user profiles with pagination and optional filtering",
    response_description="Returns a list of public user profiles",
    responses={
        200: {
            "description": "Profiles retrieved successfully",
            "model": List[ProfilePublic]
        },
        422: {
            "description": "Invalid query parameters",
            "content": {
                "application/json": {
                    "example": {"detail": [{"loc": ["query", "limit"], "msg": "ensure this value is greater than 0"}]}
                }
            }
        }
    }
)
def get_all_profiles(
    limit: int = Query(20, ge=1, le=100, description="Number of profiles to return (1-100)"),
    offset: int = Query(0, ge=0, description="Number of profiles to skip"),
    university: Optional[str] = Query(None, description="Filter by university name"),
    major: Optional[str] = Query(None, description="Filter by major"),
    current_role: Optional[str] = Query(None, description="Filter by current role"),
    gender: Optional[str] = Query(None, description="Filter by gender"),
    religion: Optional[str] = Query(None, description="Filter by religion"),
    db: Session = Depends(get_db)
):
    """
    **Get All User Profiles**
    
    Retrieve a paginated list of all user profiles with optional filtering capabilities.
    This endpoint returns public profile information (excluding sensitive data like email and date of birth).
    
    **Query Parameters:**
    - `limit`: Number of profiles to return (1-100, default: 20)
    - `offset`: Number of profiles to skip for pagination (default: 0)
    - `university`: Filter profiles by university name (optional)
    - `major`: Filter profiles by academic major (optional)
    - `current_role`: Filter by current role - student, alumni, faculty, staff, visiting_scholar (optional)
    - `gender`: Filter by gender - male, female (optional)
    - `religion`: Filter by religion - islam, hindu, christian, other (optional)
    
    **Pagination:**
    - Use `limit` to control how many profiles are returned
    - Use `offset` to skip profiles for pagination
    - Example: `?limit=10&offset=20` returns profiles 21-30
    
    **Filtering:**
    - Multiple filters can be combined
    - All filters are case-insensitive partial matches
    - Example: `?university=Tech&major=Computer&gender=male`
    
    **Returns:**
    - `List[ProfilePublic]`: Array of public profile objects
    
    **Example Usage:**
    ```
    GET /api/v1/profile/all?limit=10&offset=0&university=Tech%20University&major=Computer%20Science
    ```
    
    **Response Format:**
    ```json
    [
      {
        "id": 1,
        "username": "johndoe",
        "full_name": "John Doe",
        "university": "Tech University",
        "major": "Computer Science",
        "current_role": "student",
        "gender": "male",
        "religion": "islam",
        "one_line_bio": "CS student passionate about AI",
        "hobbies": ["Coding", "Reading"],
        "interests": ["AI", "Machine Learning"],
        "dream_role": "Software Engineer"
      }
    ]
    ```
    """
    user_repo = UserRepository(db)
    
    # Build filter parameters
    filters = {}
    if university:
        filters['university'] = university
    if major:
        filters['major'] = major
    if current_role:
        filters['current_role'] = current_role
    if gender:
        filters['gender'] = gender
    if religion:
        filters['religion'] = religion
    
    # Get profiles with filters and pagination
    profiles = user_repo.get_all_profiles(limit=limit, offset=offset, **filters)
    
    return profiles


@router.get(
    "/{user_id}",
    response_model=ProfilePublic,
    status_code=status.HTTP_200_OK,
    summary="Get Public Profile",
    description="Get a user's public profile information",
    response_description="Returns the user's public profile (sensitive info excluded)"
)
def get_public_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    """
    **Get Public Profile**
    
    Retrieve the public profile information of any user. This excludes sensitive
    information like email addresses and date of birth.
    
    **Public Information Included:**
    - Basic profile info (name, username, avatar)
    - University information (university, campus, major)
    - Academic details (class, graduation year, role)
    - Public bio and interests
    - Social links
    
    **Excluded Information:**
    - Email addresses
    - Date of birth
    - Private bio
    - Account status
    
    **Returns:**
    - Public profile information
    - Safe for display to other users
    """
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return user


@router.get(
    "/search",
    response_model=List[ProfilePublic],
    status_code=status.HTTP_200_OK,
    summary="Search Profiles",
    description="Search for users based on profile criteria",
    response_description="Returns list of matching public profiles"
)
def search_profiles(
    university: Optional[str] = Query(None, description="Filter by university"),
    campus: Optional[str] = Query(None, description="Filter by campus"),
    major: Optional[str] = Query(None, description="Filter by major"),
    current_class: Optional[str] = Query(None, description="Filter by current class"),
    graduation_year: Optional[int] = Query(None, description="Filter by graduation year"),
    current_role: Optional[str] = Query(None, description="Filter by current role"),
    interests: Optional[str] = Query(None, description="Comma-separated list of interests"),
    limit: Optional[int] = Query(20, ge=1, le=100, description="Number of results to return"),
    offset: Optional[int] = Query(0, ge=0, description="Number of results to skip"),
    db: Session = Depends(get_db)
):
    """
    **Search Profiles**
    
    Search for users based on various profile criteria. Returns public profile
    information for matching users.
    
    **Search Parameters:**
    - `university`: Filter by university name
    - `campus`: Filter by campus location
    - `major`: Filter by academic major
    - `current_class`: Filter by academic year (freshman, sophomore, etc.)
    - `graduation_year`: Filter by graduation year
    - `current_role`: Filter by role (student, alumni, faculty, etc.)
    - `interests`: Comma-separated list of interests to match
    - `limit`: Number of results (1-100, default 20)
    - `offset`: Number of results to skip (for pagination)
    
    **Search Behavior:**
    - All parameters are optional
    - Multiple parameters are combined with AND logic
    - Text searches are case-insensitive partial matches
    - Interest matching checks if user has any of the specified interests
    
    **Returns:**
    - List of matching public profiles
    - Results are paginated based on limit/offset
    - Only active users are included
    """
    user_repo = UserRepository(db)
    
    # Parse interests if provided
    interest_list = None
    if interests:
        interest_list = [interest.strip() for interest in interests.split(",")]
    
    search_params = {
        "university": university,
        "campus": campus,
        "major": major,
        "current_class": current_class,
        "graduation_year": graduation_year,
        "current_role": current_role,
        "interests": interest_list,
        "limit": limit,
        "offset": offset
    }
    
    # Remove None values
    search_params = {k: v for k, v in search_params.items() if v is not None}
    
    users = user_repo.search_profiles(search_params)
    return users


@router.post(
    "/me/verify-school-email",
    response_model=ProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify School Email",
    description="Mark the user's school email as verified",
    response_description="Returns updated profile with verified school email"
)
def verify_school_email(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    **Verify School Email**
    
    Mark the user's school email as verified. This is typically called after
    the user has completed email verification through a verification link.
    
    **Authentication Required:**
    - Valid JWT token in Authorization header
    
    **Prerequisites:**
    - User must have a school_email set in their profile
    
    **Process:**
    - Sets `is_school_email_verified` to true
    - Updates the profile timestamp
    
    **Returns:**
    - Updated user profile
    - `is_school_email_verified` will be true
    
    **Error Responses:**
    - `400 Bad Request`: No school email set
    - `404 Not Found`: User not found
    """
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(current_user_id)
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if not user.school_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No school email set to verify"
        )
    
    updated_user = user_repo.update_user_profile(current_user_id, {"is_school_email_verified": True})
    return updated_user


@router.delete(
    "/me",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete My Profile",
    description="Delete the current user's account and profile",
    response_description="Account successfully deleted"
)
def delete_my_profile(
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    **Delete My Profile**
    
    Permanently delete the current user's account and all associated data.
    This action cannot be undone.
    
    **Authentication Required:**
    - Valid JWT token in Authorization header
    
    **What Gets Deleted:**
    - User account and profile
    - All profile information
    - Password reset tokens
    - Any other associated data
    
    **Security Note:**
    - This is a permanent action
    - Consider implementing a soft delete in production
    - May want to add confirmation step
    
    **Returns:**
    - 204 No Content on success
    - No response body
    """
    user_repo = UserRepository(db)
    
    success = user_repo.delete_user(current_user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    return None
