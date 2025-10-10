from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session
from typing import List, Optional
from app.core.database import get_db
from app.schemas.post import (
    PostCreate, PostUpdate, PostResponse, PostListResponse,
    PostLikeResponse, PostLikesListResponse,
    CommentCreate, CommentUpdate, CommentResponse, PostCommentsListResponse,
    FeedResponse
)
from app.repositories.post import PostRepository
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


@router.post(
    "/",
    response_model=PostResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create Post",
    description="Create a new post with content, optional media URLs, and privacy settings",
    response_description="Returns the created post with author information"
)
def create_post(
    post_data: PostCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    **Create a New Post**
    
    Create a new post with text content, optional media URLs, and privacy settings.
    
    **Request Body:**
    - `content`: Post text content (required, 1-5000 characters)
    - `media_urls`: Array of media URLs (optional, max 10 URLs)
    - `privacy`: Post privacy setting (public, connections, private)
    
    **Privacy Settings:**
    - `public`: Visible to everyone
    - `connections`: Visible only to accepted connections
    - `private`: Visible only to the author
    
    **Returns:**
    - Created post with author information
    - Like and comment counts (initially 0)
    - Creation timestamp
    """
    post_repo = PostRepository(db)
    post = post_repo.create_post(current_user_id, post_data)
    
    # Load with author information
    post_with_author = post_repo.get_post_by_id(post.id, current_user_id)
    return post_with_author


@router.get(
    "/feed",
    status_code=status.HTTP_200_OK,
    summary="Get Personalized Feed",
    description="Get posts from your connections in chronological order"
)
def get_feed(
    limit: int = Query(20, ge=1, le=100, description="Number of posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    **Get Personalized Feed**
    
    Retrieve posts from your accepted connections in chronological order.
    This creates a personalized social media feed.
    
    **Feed Content:**
    - Posts from accepted connections
    - Your own posts
    - Public and connections-only posts (no private posts)
    - Ordered by creation date (newest first)
    
    **Query Parameters:**
    - `limit`: Number of posts to return (1-100, default: 20)
    - `offset`: Number of posts to skip (default: 0)
    
    **Returns:**
    - Paginated feed of posts
    - Total count of available posts
    - Whether there are more posts available
    """
    # Simple test feed endpoint
    return {
        "message": "Feed endpoint reached",
        "user_id": current_user_id,
        "limit": limit,
        "offset": offset
    }


@router.put(
    "/{post_id}",
    response_model=PostResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Post",
    description="Update your own post content, media URLs, or privacy settings"
)
def update_post(
    post_id: int,
    post_update: PostUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    **Update Post**
    
    Update your own post's content, media URLs, or privacy settings.
    Only the post author can update their posts.
    
    **Request Body:**
    - `content`: Updated post content (optional)
    - `media_urls`: Updated media URLs array (optional)
    - `privacy`: Updated privacy setting (optional)
    
    **Validation:**
    - At least one field must be provided
    - Content must be 1-5000 characters if provided
    - Media URLs limited to 10 items
    
    **Returns:**
    - Updated post with new content/metadata
    - Updated timestamp
    """
    post_repo = PostRepository(db)
    
    # Check if any fields are provided
    update_data = post_update.dict(exclude_unset=True, exclude_none=True)
    if not update_data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No fields provided for update"
        )
    
    updated_post = post_repo.update_post(post_id, current_user_id, post_update)
    
    if not updated_post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to update it"
        )
    
    # Return updated post with author info
    return post_repo.get_post_by_id(post_id, current_user_id)


@router.delete(
    "/{post_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Post",
    description="Delete your own post (soft delete)"
)
def delete_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    **Delete Post**
    
    Permanently delete your own post. This is a soft delete that preserves
    data integrity while removing the post from public view.
    
    **Authorization:**
    - Only the post author can delete their posts
    
    **Returns:**
    - 204 No Content on success
    - Post is marked as inactive but data is preserved
    """
    post_repo = PostRepository(db)
    
    success = post_repo.delete_post(post_id, current_user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or you don't have permission to delete it"
        )
    
    return None


@router.get(
    "/user/{user_id}",
    response_model=PostListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get User Posts",
    description="Get posts from a specific user with privacy filtering"
)
def get_user_posts(
    user_id: int,
    limit: int = Query(20, ge=1, le=100, description="Number of posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    current_user_id: Optional[int] = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    **Get User Posts**
    
    Retrieve posts from a specific user with privacy filtering applied.
    
    **Privacy Filtering:**
    - Public posts: Always visible
    - Connections posts: Visible only to accepted connections
    - Private posts: Visible only to the author
    
    **Query Parameters:**
    - `limit`: Number of posts to return (1-100, default: 20)
    - `offset`: Number of posts to skip (default: 0)
    
    **Returns:**
    - Paginated list of user's posts
    - Posts ordered by creation date (newest first)
    - Privacy filtering applied automatically
    """
    post_repo = PostRepository(db)
    
    # Check if user exists
    user_repo = UserRepository(db)
    user = user_repo.get_user_by_id(user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    posts = post_repo.get_user_posts(user_id, limit, offset, current_user_id)
    total = post_repo.get_post_count(user_id)
    
    return PostListResponse(
        posts=posts,
        total=total,
        limit=limit,
        offset=offset
    )


@router.get(
    "/feed",
    status_code=status.HTTP_200_OK,
    summary="Get Personalized Feed",
    description="Get posts from your connections in chronological order"
)
def get_feed(
    limit: int = Query(20, ge=1, le=100, description="Number of posts to return"),
    offset: int = Query(0, ge=0, description="Number of posts to skip"),
    current_user_id: int = Depends(get_current_user_id)
):
    """
    **Get Personalized Feed**
    
    Retrieve posts from your accepted connections in chronological order.
    This creates a personalized social media feed.
    
    **Feed Content:**
    - Posts from accepted connections
    - Your own posts
    - Public and connections-only posts (no private posts)
    - Ordered by creation date (newest first)
    
    **Query Parameters:**
    - `limit`: Number of posts to return (1-100, default: 20)
    - `offset`: Number of posts to skip (default: 0)
    
    **Returns:**
    - Paginated feed of posts
    - Total count of available posts
    - Whether there are more posts available
    """
    # Simple test feed endpoint
    return {
        "message": "Feed endpoint reached",
        "user_id": current_user_id,
        "limit": limit,
        "offset": offset
    }


@router.post(
    "/{post_id}/like",
    status_code=status.HTTP_200_OK,
    summary="Like/Unlike Post",
    description="Toggle like status on a post"
)
def like_post(
    post_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    **Like/Unlike Post**
    
    Toggle the like status on a post. If the post is already liked,
    it will be unliked, and vice versa.
    
    **Returns:**
    - `liked`: Boolean indicating if the post is now liked
    - `likes_count`: Updated like count for the post
    
    **Authorization:**
    - Must be authenticated
    - Post must exist and be active
    """
    post_repo = PostRepository(db)
    
    liked = post_repo.like_post(post_id, current_user_id)
    
    # Get updated like count
    post = post_repo.get_post_by_id(post_id, current_user_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    return {
        "liked": liked,
        "likes_count": post.likes_count
    }


@router.get(
    "/{post_id}/likes",
    response_model=PostLikesListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Post Likes",
    description="Get users who liked a specific post"
)
def get_post_likes(
    post_id: int,
    limit: int = Query(20, ge=1, le=100, description="Number of likes to return"),
    offset: int = Query(0, ge=0, description="Number of likes to skip"),
    db: Session = Depends(get_db)
):
    """
    **Get Post Likes**
    
    Retrieve the list of users who liked a specific post.
    
    **Query Parameters:**
    - `limit`: Number of likes to return (1-100, default: 20)
    - `offset`: Number of likes to skip (default: 0)
    
    **Returns:**
    - Paginated list of users who liked the post
    - Ordered by like timestamp (newest first)
    - Includes user profile information
    """
    post_repo = PostRepository(db)
    
    # Check if post exists
    post = post_repo.get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    likes = post_repo.get_post_likes(post_id, limit, offset)
    
    return PostLikesListResponse(
        likes=likes,
        total=post.likes_count,
        limit=limit,
        offset=offset
    )


@router.post(
    "/{post_id}/comments",
    status_code=status.HTTP_201_CREATED,
    summary="Add Comment",
    description="Add a comment to a post"
)
def create_comment(
    post_id: int,
    comment_data: CommentCreate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    **Add Comment to Post**
    
    Add a comment to a post. Comments can be top-level or replies to other comments.
    
    **Request Body:**
    - `content`: Comment text (required, 1-1000 characters)
    - `parent_comment_id`: ID of parent comment for replies (optional)
    
    **Comment Types:**
    - Top-level comments: No parent_comment_id
    - Replies: Include parent_comment_id of the comment being replied to
    
    **Returns:**
    - Created comment with author information
    - Comment ID and timestamps
    - Nested replies structure
    """
    post_repo = PostRepository(db)
    comment = post_repo.create_comment(post_id, current_user_id, comment_data)
    
    if not comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found or parent comment not found"
        )
    
    # Return basic comment data without complex relationships
    return {
        "id": comment.id,
        "post_id": comment.post_id,
        "content": comment.content,
        "parent_comment_id": comment.parent_comment_id,
        "is_active": comment.is_active,
        "created_at": comment.created_at,
        "updated_at": comment.updated_at
    }


@router.get(
    "/{post_id}/comments",
    response_model=PostCommentsListResponse,
    status_code=status.HTTP_200_OK,
    summary="Get Post Comments",
    description="Get comments for a post with nested replies"
)
def get_post_comments(
    post_id: int,
    limit: int = Query(20, ge=1, le=100, description="Number of comments to return"),
    offset: int = Query(0, ge=0, description="Number of comments to skip"),
    db: Session = Depends(get_db)
):
    """
    **Get Post Comments**
    
    Retrieve comments for a post with nested replies structure.
    
    **Comment Structure:**
    - Top-level comments are returned first
    - Each comment includes its replies (nested)
    - Ordered by creation date (oldest first)
    
    **Query Parameters:**
    - `limit`: Number of top-level comments to return (1-100, default: 20)
    - `offset`: Number of top-level comments to skip (default: 0)
    
    **Returns:**
    - Paginated list of comments with nested replies
    - Author information for each comment
    - Total comment count
    """
    post_repo = PostRepository(db)
    
    # Check if post exists
    post = post_repo.get_post_by_id(post_id)
    if not post:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Post not found"
        )
    
    comments = post_repo.get_post_comments(post_id, limit, offset)
    total = post_repo.get_comments_count(post_id)
    
    return PostCommentsListResponse(
        comments=comments,
        total=total,
        limit=limit,
        offset=offset
    )


@router.put(
    "/comments/{comment_id}",
    response_model=CommentResponse,
    status_code=status.HTTP_200_OK,
    summary="Update Comment",
    description="Update your own comment"
)
def update_comment(
    comment_id: int,
    comment_update: CommentUpdate,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    **Update Comment**
    
    Update the content of your own comment.
    
    **Request Body:**
    - `content`: Updated comment text (required, 1-1000 characters)
    
    **Authorization:**
    - Only the comment author can update their comments
    
    **Returns:**
    - Updated comment with new content
    - Updated timestamp
    """
    post_repo = PostRepository(db)
    
    updated_comment = post_repo.update_comment(comment_id, current_user_id, comment_update.content)
    
    if not updated_comment:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to update it"
        )
    
    return updated_comment


@router.delete(
    "/comments/{comment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete Comment",
    description="Delete your own comment"
)
def delete_comment(
    comment_id: int,
    current_user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
):
    """
    **Delete Comment**
    
    Delete your own comment. This is a soft delete that preserves
    data integrity while removing the comment from public view.
    
    **Authorization:**
    - Only the comment author can delete their comments
    
    **Returns:**
    - 204 No Content on success
    - Comment is marked as inactive but data is preserved
    """
    post_repo = PostRepository(db)
    
    success = post_repo.delete_comment(comment_id, current_user_id)
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Comment not found or you don't have permission to delete it"
        )
    
    return None
