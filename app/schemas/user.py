from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID # For UUID fields

# Base schema with common fields
class UserBase(BaseModel):
    full_name: str
    email: EmailStr
    phone_number: str # Add custom validation later for Kenyan format

# Schema for creating a new user (participant registration)
class UserCreate(UserBase):
    password: str = Field(..., min_length=8)
    # Status and created_at/updated_at are set by the backend

# Schema for updating user profile (optional fields)
class UserUpdate(UserBase):
    full_name: Optional[str] = None
    email: Optional[EmailStr] = None
    phone_number: Optional[str] = None
    # Password updates would typically go through a separate endpoint
    # Status might be updatable by admin

# Schema for user response (excluding sensitive fields)
class UserResponse(UserBase):
    id: UUID
    status: str # Or an Enum string
    created_at: str # Use datetime or string depending on desired output format
    updated_at: str # Use datetime or string depending on desired output format

    class Config:
        from_attributes = True # Alias: allow ORM models to be converted to schema

# Schema for participant profile response (from TDD 2.5)
class ParticipantProfileResponse(BaseModel):
    id: UUID
    full_name: str
    email: EmailStr
    phone_number: str

    class Config:
        from_attributes = True
