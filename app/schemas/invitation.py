from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from uuid import UUID
from datetime import datetime # For datetime fields

from app.models.invitation import InvitationStatus # Import InvitationStatus

# Base schema for Invitation
class InvitationBase(BaseModel):
    email: EmailStr

# Schema for creating an Invitation (by admin) - includes fields set by backend logic
class InvitationCreate(InvitationBase):
    token: str
    expires_at: datetime
    status: InvitationStatus = InvitationStatus.PENDING # Add status with default value

# Schema for Invitation response (e.g., for admin view)
class InvitationResponse(InvitationBase):
    id: UUID
    token: str # Sensitive, should be handled carefully (maybe only expose when creating)
    status: InvitationStatus # Use the Enum type
    expires_at: datetime
    created_at: datetime

    class Config:
        from_attributes = True

# Alias for the response when creating an invitation
InvitationCreateResponse = InvitationResponse
