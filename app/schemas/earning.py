from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal

# --- Earning Schemas ---

# Base schema for Earning
class EarningBase(BaseModel):
    referral_id: UUID # Link to the referral that generated it
    user_id: UUID # Link to the user who earns (denormalized)
    payment_id: Optional[UUID] = None # Null until included in a payment batch
    amount: Decimal = Field(..., decimal_places=2) # Fixed amount (50 KSH)
    due_date: date # Date eligible for payout

# Schema for creating an Earning (handled internally upon conversion)
class EarningCreate(EarningBase):
    # status, created_at/updated_at set by backend
    pass

# Schema for Earning response (for participant earnings history)
class EarningResponse(EarningBase):
    id: UUID
    status: str # Or an Enum string from models.earning
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
