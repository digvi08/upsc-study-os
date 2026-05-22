"""User schemas."""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
import uuid


class UserBase(BaseModel):
    email: EmailStr
    username: str
    full_name: str
    exam_target: str = "upsc"
    daily_study_hours: int = 8
    exam_year: Optional[int] = None
    bio: Optional[str] = None


class UserCreate(UserBase):
    password: str


class UserUpdate(BaseModel):
    full_name: Optional[str] = None
    bio: Optional[str] = None
    exam_target: Optional[str] = None
    daily_study_hours: Optional[int] = None
    exam_year: Optional[int] = None
    profile_picture: Optional[str] = None


class UserResponse(UserBase):
    id: uuid.UUID
    profile_picture: Optional[str] = None
    is_active: bool
    is_verified: bool
    role: str
    current_streak: int
    longest_streak: int
    total_study_hours: int
    created_at: datetime

    model_config = {"from_attributes": True}


class UserProfileResponse(UserResponse):
    """Extended profile with analytics."""
    total_topics_completed: Optional[int] = 0
    total_notes: Optional[int] = 0
    total_revisions: Optional[int] = 0
