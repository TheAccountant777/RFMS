from sqlalchemy import Column, Integer, Numeric, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from datetime import datetime

from .base import Base
from .database_utils import GUID, get_datetime_default
from .user import User # Import User for ForeignKey
# from .earning import Earning # Removed direct import to break circular dependency

class PaymentStatus(enum.Enum):
    PENDING_DISBURSEMENT = "PENDING_DISBURSEMENT" # Created by RPC, awaiting admin approval
    PROCESSING = "PROCESSING" # Admin approved, M-Pesa payout in progress
    SUCCESS = "SUCCESS" # M-Pesa payout successful
    FAILED = "FAILED" # M-Pesa payout failed

class Payment(Base):
    __tablename__ = 'payments'
    __table_args__ = {'schema': 'referral'} # Map to the referral schema

    id = Column(GUID(), primary_key=True)
    batch_id = Column(GUID(), nullable=False) # Groups payments into a logical batch, set by RPC
    user_id = Column(GUID(), ForeignKey('referral.users.id', ondelete='RESTRICT'), nullable=False) # Foreign key referencing referral.users
    total_amount = Column(Numeric(10, 2), nullable=False) # Total sum of earnings in this payment
    mpesa_transaction_id = Column(Text, nullable=True, unique=True) # M-Pesa transaction ID for reconciliation
    status = Column(Enum(PaymentStatus, name='payment_status'), nullable=False, server_default=PaymentStatus.PENDING_DISBURSEMENT.value)
    processed_at = Column(DateTime(timezone=True), nullable=True) # Timestamp of M-Pesa payout completion
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=get_datetime_default())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=get_datetime_default())

    def __init__(self, **kwargs):
        # Generate UUID if not provided (for SQLite compatibility)
        if 'id' not in kwargs:
            kwargs['id'] = uuid.uuid4()
        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.utcnow()
        if 'updated_at' not in kwargs:
            kwargs['updated_at'] = datetime.utcnow()
        super().__init__(**kwargs)

    # Relationships
    user = relationship("User", back_populates="payments")
    earnings = relationship("Earning", back_populates="payment")
