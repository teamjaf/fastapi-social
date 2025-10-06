from pydantic import BaseModel, EmailStr, validator
from typing import Optional, List, Dict, Any
from datetime import date
from enum import Enum


class EnrollmentStatus(str, Enum):
    ENROLLED = "enrolled"
    GRADUATED = "graduated"
    DROPPED_OUT = "dropped_out"
    ON_LEAVE = "on_leave"
    TRANSFERRED = "transferred"


class CurrentClass(str, Enum):
    FRESHMAN = "freshman"
    SOPHOMORE = "sophomore"
    JUNIOR = "junior"
    SENIOR = "senior"
    GRADUATE = "graduate"
    PHD = "phd"
    POSTDOC = "postdoc"


class CurrentRole(str, Enum):
    STUDENT = "student"
    ALUMNI = "alumni"
    FACULTY = "faculty"
    STAFF = "staff"
    VISITING_SCHOLAR = "visiting_scholar"


class ProfileBase(BaseModel):
    full_name: Optional[str] = None
    school_email: Optional[EmailStr] = None
    avatar_url: Optional[str] = None
    university: Optional[str] = None
    campus: Optional[str] = None
    enrollment_status: Optional[EnrollmentStatus] = None
    major: Optional[str] = None
    current_class: Optional[CurrentClass] = None
    graduation_year: Optional[int] = None
    current_role: Optional[CurrentRole] = None
    current_organization: Optional[str] = None
    dob: Optional[date] = None
    one_line_bio: Optional[str] = None
    full_bio: Optional[str] = None
    hobbies: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    dream_role: Optional[str] = None
    links: Optional[List[Dict[str, str]]] = None

    @validator('graduation_year')
    def validate_graduation_year(cls, v):
        if v is not None:
            current_year = 2024
            if v < 1900 or v > current_year + 10:
                raise ValueError('Graduation year must be between 1900 and 2034')
        return v

    @validator('dob')
    def validate_dob(cls, v):
        if v is not None:
            if v > date.today():
                raise ValueError('Date of birth cannot be in the future')
        return v

    @validator('links')
    def validate_links(cls, v):
        if v is not None:
            for link in v:
                if not isinstance(link, dict) or 'url' not in link:
                    raise ValueError('Each link must have a url field')
        return v


class ProfileCreate(ProfileBase):
    pass


class ProfileUpdate(ProfileBase):
    pass


class ProfileResponse(ProfileBase):
    id: int
    username: str
    email: str
    is_school_email_verified: bool
    is_active: bool
    created_at: str
    updated_at: Optional[str] = None

    class Config:
        from_attributes = True


class ProfilePublic(BaseModel):
    """Public profile view - excludes sensitive information"""
    id: int
    username: str
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    university: Optional[str] = None
    campus: Optional[str] = None
    enrollment_status: Optional[EnrollmentStatus] = None
    major: Optional[str] = None
    current_class: Optional[CurrentClass] = None
    graduation_year: Optional[int] = None
    current_role: Optional[CurrentRole] = None
    one_line_bio: Optional[str] = None
    hobbies: Optional[List[str]] = None
    interests: Optional[List[str]] = None
    dream_role: Optional[str] = None
    links: Optional[List[Dict[str, str]]] = None

    class Config:
        from_attributes = True


class ProfileSearch(BaseModel):
    university: Optional[str] = None
    campus: Optional[str] = None
    major: Optional[str] = None
    current_class: Optional[CurrentClass] = None
    graduation_year: Optional[int] = None
    current_role: Optional[CurrentRole] = None
    interests: Optional[List[str]] = None
    limit: Optional[int] = 20
    offset: Optional[int] = 0

    @validator('limit')
    def validate_limit(cls, v):
        if v is not None and (v < 1 or v > 100):
            raise ValueError('Limit must be between 1 and 100')
        return v

    @validator('offset')
    def validate_offset(cls, v):
        if v is not None and v < 0:
            raise ValueError('Offset must be non-negative')
        return v
