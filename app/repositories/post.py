from sqlalchemy.orm import Session, joinedload
from sqlalchemy import and_, or_, func, desc
from typing import List, Optional, Dict, Any
from app.models.post import Post, PostLike, PostComment
from app.models.user import User
from app.models.connection import Connection
from app.schemas.post import PostCreate, PostUpdate, CommentCreate, PostPrivacy
from app.schemas.connection import ConnectionStatus
from datetime import datetime


class PostRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_post(self, user_id: int, post_data: PostCreate) -> Post:
        """Create a new post"""
        try:
            post = Post(
                user_id=user_id,
                content=post_data.content,
                media_urls=post_data.media_urls,
                privacy=post_data.privacy.value
            )
            self.db.add(post)
            self.db.commit()
            self.db.refresh(post)
            return post
        except Exception as e:
            self.db.rollback()
            raise e

    def get_post_by_id(self, post_id: int, current_user_id: Optional[int] = None) -> Optional[Post]:
        """Get single post with author and like count"""
        query = self.db.query(Post).options(
            joinedload(Post.author)
        ).filter(
            and_(Post.id == post_id, Post.is_active == True)
        )
        
        post = query.first()
        if not post:
            return None
        
        # Check if current user liked this post
        if current_user_id:
            post.is_liked = self.check_user_liked(post_id, current_user_id)
        else:
            post.is_liked = False
            
        return post

    def update_post(self, post_id: int, user_id: int, update_data: PostUpdate) -> Optional[Post]:
        """Update own post"""
        post = self.db.query(Post).filter(
            and_(Post.id == post_id, Post.user_id == user_id, Post.is_active == True)
        ).first()
        
        if not post:
            return None
        
        # Update fields if provided
        if update_data.content is not None:
            post.content = update_data.content
        if update_data.media_urls is not None:
            post.media_urls = update_data.media_urls
        if update_data.privacy is not None:
            post.privacy = update_data.privacy.value
        
        post.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(post)
        return post

    def delete_post(self, post_id: int, user_id: int) -> bool:
        """Soft delete own post"""
        post = self.db.query(Post).filter(
            and_(Post.id == post_id, Post.user_id == user_id, Post.is_active == True)
        ).first()
        
        if not post:
            return False
        
        post.is_active = False
        post.updated_at = datetime.utcnow()
        self.db.commit()
        return True

    def get_user_posts(self, user_id: int, limit: int = 20, offset: int = 0, current_user_id: Optional[int] = None) -> List[Post]:
        """Get user's posts with privacy filtering"""
        query = self.db.query(Post).options(
            joinedload(Post.author)
        ).filter(
            and_(Post.user_id == user_id, Post.is_active == True)
        )
        
        # Privacy filtering
        if current_user_id != user_id:  # Not viewing own posts
            # Only show public posts or posts from connections
            query = query.filter(
                or_(
                    Post.privacy == PostPrivacy.PUBLIC.value,
                    and_(
                        Post.privacy == PostPrivacy.CONNECTIONS.value,
                        self._is_connected(current_user_id, user_id)
                    )
                )
            )
        
        posts = query.order_by(desc(Post.created_at)).offset(offset).limit(limit).all()
        
        # Check if current user liked each post
        if current_user_id:
            for post in posts:
                post.is_liked = self.check_user_liked(post.id, current_user_id)
        else:
            for post in posts:
                post.is_liked = False
        
        return posts

    def get_feed(self, user_id: int, limit: int = 20, offset: int = 0) -> List[Post]:
        """Get personalized feed from connections"""
        # Get user's accepted connections
        connections_query = self.db.query(Connection).filter(
            and_(
                or_(
                    Connection.requester_id == user_id,
                    Connection.addressee_id == user_id
                ),
                Connection.status == ConnectionStatus.ACCEPTED
            )
        )
        
        connected_user_ids = set()
        for conn in connections_query.all():
            if conn.requester_id == user_id:
                connected_user_ids.add(conn.addressee_id)
            else:
                connected_user_ids.add(conn.requester_id)
        
        # Include own posts
        connected_user_ids.add(user_id)
        
        # Get posts from connections (public and connections privacy)
        posts = self.db.query(Post).options(
            joinedload(Post.author)
        ).filter(
            and_(
                Post.user_id.in_(connected_user_ids),
                Post.is_active == True,
                Post.privacy.in_([PostPrivacy.PUBLIC.value, PostPrivacy.CONNECTIONS.value])
            )
        ).order_by(desc(Post.created_at)).offset(offset).limit(limit).all()
        
        # Check if current user liked each post
        for post in posts:
            post.is_liked = self.check_user_liked(post.id, user_id)
        
        return posts

    def get_public_posts(self, limit: int = 20, offset: int = 0, current_user_id: Optional[int] = None) -> List[Post]:
        """Get all public posts"""
        posts = self.db.query(Post).options(
            joinedload(Post.author)
        ).filter(
            and_(Post.privacy == PostPrivacy.PUBLIC.value, Post.is_active == True)
        ).order_by(desc(Post.created_at)).offset(offset).limit(limit).all()
        
        # Check if current user liked each post
        if current_user_id:
            for post in posts:
                post.is_liked = self.check_user_liked(post.id, current_user_id)
        else:
            for post in posts:
                post.is_liked = False
        
        return posts

    def like_post(self, post_id: int, user_id: int) -> bool:
        """Like/unlike post (toggle)"""
        # Check if post exists and is active
        post = self.db.query(Post).filter(
            and_(Post.id == post_id, Post.is_active == True)
        ).first()
        
        if not post:
            return False
        
        # Check if already liked
        existing_like = self.db.query(PostLike).filter(
            and_(PostLike.post_id == post_id, PostLike.user_id == user_id)
        ).first()
        
        if existing_like:
            # Unlike - remove the like
            self.db.delete(existing_like)
            post.likes_count = max(0, post.likes_count - 1)
            self.db.commit()
            return False
        else:
            # Like - add the like
            like = PostLike(post_id=post_id, user_id=user_id)
            self.db.add(like)
            post.likes_count += 1
            self.db.commit()
            return True

    def get_post_likes(self, post_id: int, limit: int = 20, offset: int = 0) -> List[PostLike]:
        """Get users who liked a post"""
        return self.db.query(PostLike).options(
            joinedload(PostLike.user)
        ).filter(PostLike.post_id == post_id).order_by(
            desc(PostLike.created_at)
        ).offset(offset).limit(limit).all()

    def check_user_liked(self, post_id: int, user_id: int) -> bool:
        """Check if user liked a post"""
        like = self.db.query(PostLike).filter(
            and_(PostLike.post_id == post_id, PostLike.user_id == user_id)
        ).first()
        return like is not None

    def create_comment(self, post_id: int, user_id: int, comment_data: CommentCreate) -> Optional[PostComment]:
        """Add comment to post"""
        # Check if post exists and is active
        post = self.db.query(Post).filter(
            and_(Post.id == post_id, Post.is_active == True)
        ).first()
        
        if not post:
            return None
        
        # Check if parent comment exists (for replies)
        if comment_data.parent_comment_id:
            parent_comment = self.db.query(PostComment).filter(
                and_(
                    PostComment.id == comment_data.parent_comment_id,
                    PostComment.post_id == post_id,
                    PostComment.is_active == True
                )
            ).first()
            if not parent_comment:
                return None
        
        comment = PostComment(
            post_id=post_id,
            user_id=user_id,
            content=comment_data.content,
            parent_comment_id=comment_data.parent_comment_id
        )
        
        self.db.add(comment)
        post.comments_count += 1
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def get_comment_by_id(self, comment_id: int) -> Optional[PostComment]:
        """Get comment by ID with author information"""
        return self.db.query(PostComment).options(
            joinedload(PostComment.author)
        ).filter(
            and_(PostComment.id == comment_id, PostComment.is_active == True)
        ).first()

    def update_comment(self, comment_id: int, user_id: int, content: str) -> Optional[PostComment]:
        """Update own comment"""
        comment = self.db.query(PostComment).filter(
            and_(
                PostComment.id == comment_id,
                PostComment.user_id == user_id,
                PostComment.is_active == True
            )
        ).first()
        
        if not comment:
            return None
        
        comment.content = content
        comment.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(comment)
        return comment

    def delete_comment(self, comment_id: int, user_id: int) -> bool:
        """Soft delete own comment"""
        comment = self.db.query(PostComment).filter(
            and_(
                PostComment.id == comment_id,
                PostComment.user_id == user_id,
                PostComment.is_active == True
            )
        ).first()
        
        if not comment:
            return False
        
        comment.is_active = False
        comment.updated_at = datetime.utcnow()
        
        # Decrease post comment count
        post = self.db.query(Post).filter(Post.id == comment.post_id).first()
        if post:
            post.comments_count = max(0, post.comments_count - 1)
        
        self.db.commit()
        return True

    def get_post_comments(self, post_id: int, limit: int = 20, offset: int = 0) -> List[PostComment]:
        """Get comments for a post with nested replies"""
        # Get top-level comments (no parent)
        comments = self.db.query(PostComment).options(
            joinedload(PostComment.author)
        ).filter(
            and_(
                PostComment.post_id == post_id,
                PostComment.parent_comment_id.is_(None),
                PostComment.is_active == True
            )
        ).order_by(PostComment.created_at).offset(offset).limit(limit).all()
        
        # Load replies for each comment
        for comment in comments:
            comment.replies = self.get_comment_replies(comment.id, limit=10)
        
        return comments

    def get_comment_replies(self, comment_id: int, limit: int = 20, offset: int = 0) -> List[PostComment]:
        """Get nested replies to a comment"""
        return self.db.query(PostComment).options(
            joinedload(PostComment.author)
        ).filter(
            and_(
                PostComment.parent_comment_id == comment_id,
                PostComment.is_active == True
            )
        ).order_by(PostComment.created_at).offset(offset).limit(limit).all()

    def get_post_count(self, user_id: int) -> int:
        """Get total count of user's posts"""
        return self.db.query(Post).filter(
            and_(Post.user_id == user_id, Post.is_active == True)
        ).count()

    def get_feed_count(self, user_id: int) -> int:
        """Get total count of posts in user's feed"""
        # Get user's accepted connections
        connections_query = self.db.query(Connection).filter(
            and_(
                or_(
                    Connection.requester_id == user_id,
                    Connection.addressee_id == user_id
                ),
                Connection.status == ConnectionStatus.ACCEPTED
            )
        )
        
        connected_user_ids = set()
        for conn in connections_query.all():
            if conn.requester_id == user_id:
                connected_user_ids.add(conn.addressee_id)
            else:
                connected_user_ids.add(conn.requester_id)
        
        # Include own posts
        connected_user_ids.add(user_id)
        
        return self.db.query(Post).filter(
            and_(
                Post.user_id.in_(connected_user_ids),
                Post.is_active == True,
                Post.privacy.in_([PostPrivacy.PUBLIC.value, PostPrivacy.CONNECTIONS.value])
            )
        ).count()

    def get_comments_count(self, post_id: int) -> int:
        """Get total count of comments for a post"""
        return self.db.query(PostComment).filter(
            and_(PostComment.post_id == post_id, PostComment.is_active == True)
        ).count()

    def _is_connected(self, user1_id: int, user2_id: int) -> bool:
        """Check if two users are connected (accepted status)"""
        if user1_id == user2_id:
            return True
        
        connection = self.db.query(Connection).filter(
            and_(
                or_(
                    and_(Connection.requester_id == user1_id, Connection.addressee_id == user2_id),
                    and_(Connection.requester_id == user2_id, Connection.addressee_id == user1_id)
                ),
                Connection.status == ConnectionStatus.ACCEPTED
            )
        ).first()
        
        return connection is not None
