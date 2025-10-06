import secrets
import string
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from app.models.password_reset import PasswordResetToken
from app.models.user import User
from app.utils.auth import get_password_hash
from typing import Optional


def generate_reset_token() -> str:
    """Generate a secure random token for password reset"""
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for _ in range(32))


def create_password_reset_token(db: Session, user: User) -> PasswordResetToken:
    """Create a new password reset token for a user"""
    # Invalidate any existing tokens for this user
    db.query(PasswordResetToken).filter(
        PasswordResetToken.user_id == user.id,
        PasswordResetToken.is_used == False
    ).update({"is_used": True})
    
    # Create new token
    token = generate_reset_token()
    expires_at = datetime.utcnow() + timedelta(hours=1)  # Token expires in 1 hour
    
    db_token = PasswordResetToken(
        user_id=user.id,
        token=token,
        expires_at=expires_at
    )
    
    db.add(db_token)
    db.commit()
    db.refresh(db_token)
    
    return db_token


def get_valid_reset_token(db: Session, token: str) -> Optional[PasswordResetToken]:
    """Get a valid (unused and not expired) password reset token"""
    return db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token,
        PasswordResetToken.is_used == False,
        PasswordResetToken.expires_at > datetime.utcnow()
    ).first()


def use_reset_token(db: Session, token: str) -> bool:
    """Mark a reset token as used"""
    db_token = db.query(PasswordResetToken).filter(
        PasswordResetToken.token == token
    ).first()
    
    if db_token:
        db_token.is_used = True
        db.commit()
        return True
    
    return False


def reset_user_password(db: Session, user: User, new_password: str) -> bool:
    """Reset a user's password"""
    try:
        user.hashed_password = get_password_hash(new_password)
        db.commit()
        return True
    except Exception:
        db.rollback()
        return False
