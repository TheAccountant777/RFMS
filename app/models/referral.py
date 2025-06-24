from sqlalchemy import Column, Integer, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from datetime import datetime

from .base import Base
from .database_utils import GUID, get_datetime_default
from .referral_link import ReferralLink  # Import ReferralLink for ForeignKey
from .earning import Earning  # Import Earning for relationship


class ReferralStatus(enum.Enum):
    PENDING = "PENDING"  # Initial state after click, before signup
    SIGNED_UP = "SIGNED_UP"  # After user signs up on main platform
    CONVERTED = "CONVERTED"  # After user makes first payment on main platform


class Referral(Base):
    __tablename__ = 'referrals'
    __table_args__ = {'schema': 'referral'}  # Map to the referral schema

    id = Column(GUID(), primary_key=True)
    referral_link_id = Column(GUID(), ForeignKey('referral.referral_links.id',
                              ondelete='CASCADE'), nullable=False)  # Foreign key referencing referral.referral_links
    # External reference to the user ID in the main SaaS DB
    referred_user_id = Column(Text, nullable=True)
    status = Column(Enum(ReferralStatus, name='referral_status'),
                    nullable=False, server_default=ReferralStatus.PENDING.value)
    # Counter for the 6-month earning cycle
    earnings_paid_count = Column(Integer, nullable=False, server_default='0')
    # Timestamp of the initial click (or record creation)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=get_datetime_default())
    signed_up_at = Column(DateTime(timezone=True), nullable=True)
    # Timestamp of the first successful payment
    converted_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=get_datetime_default())

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
    referral_link = relationship("ReferralLink", back_populates="referrals")
    earnings = relationship("Earning", back_populates="referral")
