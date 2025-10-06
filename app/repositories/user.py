from sqlalchemy.orm import Session
from sqlalchemy import and_, or_
from app.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.utils.auth import get_password_hash, verify_password
from typing import Optional, List, Dict, Any


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_user_by_email(self, email: str) -> Optional[User]:
        """Get user by email"""
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_username(self, username: str) -> Optional[User]:
        """Get user by username"""
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """Get user by ID"""
        return self.db.query(User).filter(User.id == user_id).first()

    def create_user(self, user: UserCreate) -> User:
        """Create a new user"""
        hashed_password = get_password_hash(user.password)
        db_user = User(
            email=user.email,
            username=user.username,
            full_name=user.full_name,
            hashed_password=hashed_password
        )
        self.db.add(db_user)
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user(self, user_id: int, user_update: UserUpdate) -> Optional[User]:
        """Update user information"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None
        
        update_data = user_update.dict(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def update_user_profile(self, user_id: int, profile_data: Dict[str, Any]) -> Optional[User]:
        """Update user profile information"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return None
        
        # Update only the provided fields
        for field, value in profile_data.items():
            if hasattr(db_user, field):
                setattr(db_user, field, value)
        
        self.db.commit()
        self.db.refresh(db_user)
        return db_user

    def search_profiles(self, search_params: Dict[str, Any]) -> List[User]:
        """Search users based on profile criteria"""
        query = self.db.query(User).filter(User.is_active == True)
        
        # Apply filters
        if search_params.get("university"):
            query = query.filter(User.university.ilike(f"%{search_params['university']}%"))
        
        if search_params.get("campus"):
            query = query.filter(User.campus.ilike(f"%{search_params['campus']}%"))
        
        if search_params.get("major"):
            query = query.filter(User.major.ilike(f"%{search_params['major']}%"))
        
        if search_params.get("current_class"):
            query = query.filter(User.current_class == search_params["current_class"])
        
        if search_params.get("graduation_year"):
            query = query.filter(User.graduation_year == search_params["graduation_year"])
        
        if search_params.get("current_role"):
            query = query.filter(User.current_role == search_params["current_role"])
        
        if search_params.get("interests"):
            # Search for users who have any of the specified interests
            interest_conditions = []
            for interest in search_params["interests"]:
                interest_conditions.append(User.interests.op('?')(interest))
            if interest_conditions:
                query = query.filter(or_(*interest_conditions))
        
        # Apply pagination
        offset = search_params.get("offset", 0)
        limit = search_params.get("limit", 20)
        
        return query.offset(offset).limit(limit).all()

    def delete_user(self, user_id: int) -> bool:
        """Delete user account"""
        db_user = self.get_user_by_id(user_id)
        if not db_user:
            return False
        
        self.db.delete(db_user)
        self.db.commit()
        return True

    def authenticate_user(self, email: str, password: str) -> Optional[User]:
        """Authenticate user with email and password"""
        user = self.get_user_by_email(email)
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user
