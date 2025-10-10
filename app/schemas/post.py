from pydantic import BaseModel, validator, Field
from typing import Optional, List
from datetime import datetime
from enum import Enum
from app.schemas.profile import ProfilePublic


class PostPrivacy(str, Enum):
    PUBLIC = "public"
    CONNECTIONS = "connections"
    PRIVATE = "private"


class PostBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=5000, description="Post content")
    media_urls: Optional[List[str]] = Field(None, description="Array of media URLs")
    privacy: PostPrivacy = Field(PostPrivacy.PUBLIC, description="Post privacy setting")

    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()

    @validator('media_urls')
    def validate_media_urls(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError('Maximum 10 media URLs allowed')
            for url in v:
                if not url or not url.strip():
                    raise ValueError('Media URL cannot be empty')
        return v


class PostCreate(PostBase):
    pass


class PostUpdate(BaseModel):
    content: Optional[str] = Field(None, min_length=1, max_length=5000)
    media_urls: Optional[List[str]] = Field(None)
    privacy: Optional[PostPrivacy] = None

    @validator('content')
    def validate_content(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Content cannot be empty')
            return v.strip()
        return v

    @validator('media_urls')
    def validate_media_urls(cls, v):
        if v is not None:
            if len(v) > 10:
                raise ValueError('Maximum 10 media URLs allowed')
            for url in v:
                if not url or not url.strip():
                    raise ValueError('Media URL cannot be empty')
        return v


class PostResponse(BaseModel):
    id: int
    author: ProfilePublic
    content: str
    media_urls: Optional[List[str]] = None
    privacy: PostPrivacy
    likes_count: int
    comments_count: int
    is_liked: bool = False  # Whether current user liked this post
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PostListResponse(BaseModel):
    posts: List[PostResponse]
    total: int
    limit: int
    offset: int

    class Config:
        from_attributes = True


class PostLikeResponse(BaseModel):
    id: int
    user: ProfilePublic
    created_at: datetime

    class Config:
        from_attributes = True


class PostLikesListResponse(BaseModel):
    likes: List[PostLikeResponse]
    total: int
    limit: int
    offset: int

    class Config:
        from_attributes = True


class CommentBase(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000, description="Comment content")

    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()


class CommentCreate(CommentBase):
    parent_comment_id: Optional[int] = Field(None, description="ID of parent comment for replies")


class CommentUpdate(BaseModel):
    content: str = Field(..., min_length=1, max_length=1000)

    @validator('content')
    def validate_content(cls, v):
        if not v or not v.strip():
            raise ValueError('Content cannot be empty')
        return v.strip()


class CommentResponse(BaseModel):
    id: int
    author: ProfilePublic
    content: str
    parent_comment_id: Optional[int] = None
    replies: List['CommentResponse'] = []
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class PostCommentsListResponse(BaseModel):
    comments: List[CommentResponse]
    total: int
    limit: int
    offset: int

    class Config:
        from_attributes = True


class FeedResponse(BaseModel):
    posts: List[PostResponse]
    total: int
    limit: int
    offset: int
    has_more: bool

    class Config:
        from_attributes = True


# Update forward references
CommentResponse.model_rebuild()
