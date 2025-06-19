from sqlalchemy import Column, Integer, Numeric, Text, ForeignKey, Enum, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base
# from .referral import Referral # Removed direct import to break circular dependency
from .user import User # Import User for ForeignKey (denormalized)
from .payment import Payment # Import Payment for ForeignKey

import enum

class EarningStatus(enum.Enum):
    SCHEDULED = "SCHEDULEED" # Created when referral converts, eligible after due_date
    PENDING_APPROVAL = "PENDING_APPROVAL" # Included in a payment batch, awaiting admin approval
    PAID = "PAID" # Included in a payment batch, M-Pesa payout successful
    FAILED = "FAILED" # Included in a payment batch, M-Pesa payout failed

class Earning(Base):
    __tablename__ = 'earnings'
    __table_args__ = {'schema': 'referral'} # Map to the referral schema

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    referral_id = Column(UUID(as_uuid=True), ForeignKey('referral.referrals.id', ondelete='CASCADE'), nullable=False) # Foreign key referencing referral.referrals
    user_id = Column(UUID(as_uuid=True), ForeignKey('referral.users.id', ondelete='RESTRICT'), nullable=False) # Foreign key referencing referral.users (denormalized)
    payment_id = Column(UUID(as_uuid=True), ForeignKey('referral.payments.id', ondelete='SET NULL'), nullable=True) # Foreign key referencing referral.payments, Null until included in a payment batch
    amount = Column(Numeric(10, 2), nullable=False, server_default='50.00') # Fixed amount as per CDD
    status = Column(Enum(EarningStatus, name='earning_status'), nullable=False, server_default=EarningStatus.SCHEDULED.value)
    due_date = Column(Date, nullable=False) # Date earning becomes eligible for payout
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    referral = relationship("Referral", back_populates="earnings")
    user = relationship("User", back_populates="earnings")
    payment = relationship("Payment", back_populates="earnings")
