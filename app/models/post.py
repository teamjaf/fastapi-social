from sqlalchemy import Column, Integer, String, DateTime, Boolean, Text, JSON, ForeignKey, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class Post(Base):
    __tablename__ = "posts"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign key to users table
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Post content
    content = Column(Text, nullable=False)
    media_urls = Column(JSON, nullable=True)  # Array of image/video URLs
    
    # Privacy settings
    privacy = Column(String(20), nullable=False, default="public")  # public, connections, private
    
    # Status and counts
    is_active = Column(Boolean, default=True)
    likes_count = Column(Integer, default=0)
    comments_count = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    author = relationship("User", backref="posts")
    likes = relationship("PostLike", back_populates="post", cascade="all, delete-orphan")
    comments = relationship("PostComment", back_populates="post", cascade="all, delete-orphan")


class PostLike(Base):
    __tablename__ = "post_likes"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Timestamp
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    post = relationship("Post", back_populates="likes")
    user = relationship("User", backref="post_likes")
    
    # Constraints
    __table_args__ = (
        UniqueConstraint('post_id', 'user_id', name='unique_post_like'),
    )


class PostComment(Base):
    __tablename__ = "post_comments"

    # Primary key
    id = Column(Integer, primary_key=True, index=True)
    
    # Foreign keys
    post_id = Column(Integer, ForeignKey("posts.id"), nullable=False, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Comment content
    content = Column(Text, nullable=False)
    
    # For nested replies
    parent_comment_id = Column(Integer, ForeignKey("post_comments.id"), nullable=True, index=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    post = relationship("Post", back_populates="comments")
    author = relationship("User", backref="post_comments")
    parent_comment = relationship("PostComment", remote_side=[id], backref="replies")
