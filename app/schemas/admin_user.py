from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID  # For UUID fields
from datetime import datetime  # For datetime fields

# Base schema for AdminUser
class AdminUserBase(BaseModel):
    email: EmailStr
    role: str  # Or an Enum string from models.admin_user

# Schema for creating a new AdminUser (likely via script or internal tool)
class AdminUserCreate(AdminUserBase):
    password: str = Field(..., min_length=8)
    # created_at/updated_at are set by backend

# Schema for updating AdminUser
class AdminUserUpdate(AdminUserBase):
    email: Optional[EmailStr] = None
    role: Optional[str] = None
    # Password updates would typically go through a separate endpoint

# Schema for AdminUser response (excluding sensitive fields)
class AdminUserResponse(AdminUserBase):
    id: UUID
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True  # Alias: allow ORM models to be converted to schema
