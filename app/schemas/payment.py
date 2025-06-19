from pydantic import BaseModel, Field
from typing import Optional, List
from uuid import UUID
from datetime import datetime
from decimal import Decimal

# --- Payment Schemas ---

# Base schema for Payment
class PaymentBase(BaseModel):
    batch_id: UUID # Link to the payment batch
    user_id: UUID # Link to the user receiving payment
    total_amount: Decimal = Field(..., decimal_places=2)
    mpesa_transaction_id: Optional[str] = None # Can be null initially

# Schema for creating a Payment (likely handled by RPC/internal logic)
class PaymentCreate(PaymentBase):
    # status, processed_at, created_at/updated_at set by backend
    pass

# Schema for Payment response (for admin or participant history)
class PaymentResponse(PaymentBase):
    id: UUID
    status: str # Or an Enum string from models.payment
    processed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
