from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime, date # For datetime and date fields
from decimal import Decimal # For Decimal fields

# --- ReferralLink Schemas ---

# Base schema for ReferralLink
class ReferralLinkBase(BaseModel):
    unique_code: str

# Schema for creating a ReferralLink (handled internally upon user creation)
class ReferralLinkCreate(ReferralLinkBase):
    user_id: UUID # Link to the user
    # click_count, conversion_count, status, created_at/updated_at set by backend

# Schema for ReferralLink response (for participant dashboard)
class ReferralLinkResponse(ReferralLinkBase):
    id: UUID
    user_id: UUID
    click_count: int
    conversion_count: int
    status: str # Or an Enum string
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Referral Schemas ---

# Base schema for Referral
class ReferralBase(BaseModel):
    referral_link_id: UUID # Link to the referral link
    referred_user_id: Optional[str] = None # External ID from main SaaS

# Schema for creating a Referral (handled internally after click/signup)
class ReferralCreate(ReferralBase):
    # status, earnings_paid_count, timestamps set by backend
    pass

# Schema for Referral response (for admin view/audit)
class ReferralResponse(ReferralBase):
    id: UUID
    status: str # Or an Enum string
    earnings_paid_count: int
    created_at: datetime
    signed_up_at: Optional[datetime] = None
    converted_at: Optional[datetime] = None
    updated_at: datetime

    class Config:
        from_attributes = True

# --- Specific API Response Schema (from TDD 2.6) ---

class ParticipantStatsResponse(BaseModel):
    clicks: int
    signups: int # Note: TDD schema uses 'signups', model uses 'status' on Referral. Need to map.
    conversions: int
    earnings_scheduled: Decimal = Field(..., decimal_places=2) # Sum of earnings with status \'SCHEDULED\'
    earnings_paid: Decimal = Field(..., decimal_places=2) # Sum of earnings with status \'PAID\'

    class Config:
        # No from_attributes = True here, as this is likely computed/aggregated
        pass
