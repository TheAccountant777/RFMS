from sqlalchemy import Column, Integer, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base
from .referral_link import ReferralLink  # Import ReferralLink for ForeignKey
from .earning import Earning  # Import Earning for relationship

import enum


class ReferralStatus(enum.Enum):
    PENDING = "PENDING"  # Initial state after click, before signup
    SIGNED_UP = "SIGNED_UP"  # After user signs up on main platform
    CONVERTED = "CONVERTED"  # After user makes first payment on main platform


class Referral(Base):
    __tablename__ = 'referrals'
    __table_args__ = {'schema': 'referral'}  # Map to the referral schema

    id = Column(UUID(as_uuid=True), primary_key=True,
                server_default=func.gen_random_uuid())
    referral_link_id = Column(UUID(as_uuid=True), ForeignKey('referral.referral_links.id',
                              ondelete='CASCADE'), nullable=False)  # Foreign key referencing referral.referral_links
    # External reference to the user ID in the main SaaS DB
    referred_user_id = Column(Text, nullable=True)
    status = Column(Enum(ReferralStatus, name='referral_status'),
                    nullable=False, server_default=ReferralStatus.PENDING.value)
    # Counter for the 6-month earning cycle
    earnings_paid_count = Column(Integer, nullable=False, server_default='0')
    # Timestamp of the initial click (or record creation)
    created_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())
    signed_up_at = Column(DateTime(timezone=True), nullable=True)
    # Timestamp of the first successful payment
    converted_at = Column(DateTime(timezone=True), nullable=True)
    updated_at = Column(DateTime(timezone=True),
                        nullable=False, server_default=func.now())

    # Relationships
    referral_link = relationship("ReferralLink", back_populates="referrals")
    earnings = relationship("Earning", back_populates="referral")
