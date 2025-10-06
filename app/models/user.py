from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from app.core.database import Base


class User(Base):
    __tablename__ = "users"

    # Basic authentication fields
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    username = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Profile fields
    full_name = Column(String, nullable=True)
    school_email = Column(String, nullable=True)
    is_school_email_verified = Column(Boolean, default=False)
    avatar_url = Column(String, nullable=True)
    university = Column(String, nullable=True)
    campus = Column(String, nullable=True)
    enrollment_status = Column(String, nullable=True)  # enrolled, graduated, dropped_out, etc.
    major = Column(String, nullable=True)
    current_class = Column(String, nullable=True)  # freshman, sophomore, junior, senior, graduate
    graduation_year = Column(Integer, nullable=True)
    current_role = Column(String, nullable=True)  # student, alumni, faculty, staff
    current_organization = Column(String, nullable=True)
    dob = Column(Date, nullable=True)
    one_line_bio = Column(String, nullable=True)
    full_bio = Column(Text, nullable=True)
    hobbies = Column(JSON, nullable=True)  # Array of hobbies
    interests = Column(JSON, nullable=True)  # Array of interests
    dream_role = Column(String, nullable=True)  # Dream profession or role
    links = Column(JSON, nullable=True)  # Array of social links
    gender = Column(String, nullable=True)  # male, female
    religion = Column(String, nullable=True)  # islam, hindu, christian, other
    
    # Relationships
    password_reset_tokens = relationship("PasswordResetToken", back_populates="user")
