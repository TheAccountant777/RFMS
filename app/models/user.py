from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base
# Import other models for relationships - ensure these are imported correctly
# from .referral_link import ReferralLink
# from .payment import Payment
# from .earning import Earning

import enum

class UserStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'referral'} # Map to the referral schema

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    full_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    phone_number = Column(Text, nullable=False, unique=True) # Validation handled in Pydantic
    status = Column(Enum(UserStatus, name='user_status'), nullable=False, server_default=UserStatus.ACTIVE.value)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships (uncomment and refine once related models are confirmed to exist)
    referral_links = relationship("ReferralLink", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    earnings = relationship("Earning", back_populates="user")
