from sqlalchemy import Column, Integer, Numeric, Text, ForeignKey, Enum, DateTime, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from datetime import datetime

from .base import Base
from .database_utils import GUID, get_datetime_default
# from .referral import Referral # Removed direct import to break circular dependency
from .user import User # Import User for ForeignKey (denormalized)
from .payment import Payment # Import Payment for ForeignKey

class EarningStatus(enum.Enum):
    SCHEDULED = "SCHEDULEED" # Created when referral converts, eligible after due_date
    PENDING_APPROVAL = "PENDING_APPROVAL" # Included in a payment batch, awaiting admin approval
    PAID = "PAID" # Included in a payment batch, M-Pesa payout successful
    FAILED = "FAILED" # Included in a payment batch, M-Pesa payout failed

class Earning(Base):
    __tablename__ = 'earnings'
    __table_args__ = {'schema': 'referral'} # Map to the referral schema

    id = Column(GUID(), primary_key=True)
    referral_id = Column(GUID(), ForeignKey('referral.referrals.id', ondelete='CASCADE'), nullable=False) # Foreign key referencing referral.referrals
    user_id = Column(GUID(), ForeignKey('referral.users.id', ondelete='RESTRICT'), nullable=False) # Foreign key referencing referral.users (denormalized)
    payment_id = Column(GUID(), ForeignKey('referral.payments.id', ondelete='SET NULL'), nullable=True) # Foreign key referencing referral.payments, Null until included in a payment batch
    amount = Column(Numeric(10, 2), nullable=False, server_default='50.00') # Fixed amount as per CDD
    status = Column(Enum(EarningStatus, name='earning_status'), nullable=False, server_default=EarningStatus.SCHEDULED.value)
    due_date = Column(Date, nullable=False) # Date earning becomes eligible for payout
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
    referral = relationship("Referral", back_populates="earnings")
    user = relationship("User", back_populates="earnings")
    payment = relationship("Payment", back_populates="earnings")
