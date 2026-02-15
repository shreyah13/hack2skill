"""User-related data models."""

from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field, EmailStr


class UserCredentials(BaseModel):
    """User login credentials."""
    
    email: EmailStr
    password: str


class AuthToken(BaseModel):
    """Authentication token response."""
    
    access_token: str
    refresh_token: str
    expires_in: int
    token_type: str = "Bearer"


class UserSession(BaseModel):
    """User session information."""
    
    user_id: str
    email: EmailStr
    expires_at: datetime


class User(BaseModel):
    """User profile information."""
    
    user_id: str
    email: EmailStr
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    is_active: bool = True


class UserCreate(BaseModel):
    """User creation request."""
    
    email: EmailStr
    password: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None


class UserUpdate(BaseModel):
    """User update request."""
    
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    is_active: Optional[bool] = None
