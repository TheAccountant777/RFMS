from sqlalchemy import Column, Integer, Numeric, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base
from .user import User # Import User for ForeignKey
# from .earning import Earning # Removed direct import to break circular dependency

import enum

class PaymentStatus(enum.Enum):
    PENDING_DISBURSEMENT = "PENDING_DISBURSEMENT" # Created by RPC, awaiting admin approval
    PROCESSING = "PROCESSING" # Admin approved, M-Pesa payout in progress
    SUCCESS = "SUCCESS" # M-Pesa payout successful
    FAILED = "FAILED" # M-Pesa payout failed

class Payment(Base):
    __tablename__ = 'payments'
    __table_args__ = {'schema': 'referral'} # Map to the referral schema

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    batch_id = Column(UUID(as_uuid=True), nullable=False) # Groups payments into a logical batch, set by RPC
    user_id = Column(UUID(as_uuid=True), ForeignKey('referral.users.id', ondelete='RESTRICT'), nullable=False) # Foreign key referencing referral.users
    total_amount = Column(Numeric(10, 2), nullable=False) # Total sum of earnings in this payment
    mpesa_transaction_id = Column(Text, nullable=True, unique=True) # M-Pesa transaction ID for reconciliation
    status = Column(Enum(PaymentStatus, name='payment_status'), nullable=False, server_default=PaymentStatus.PENDING_DISBURSEMENT.value)
    processed_at = Column(DateTime(timezone=True), nullable=True) # Timestamp of M-Pesa payout completion
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships
    user = relationship("User", back_populates="payments")
    earnings = relationship("Earning", back_populates="payment")
