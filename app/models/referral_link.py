from sqlalchemy import Column, Integer, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base
# Import other models for relationships - ensure these are imported correctly
# from .user import User # Import User for ForeignKey
# from .referral import Referral # Import Referral for relationship

import enum

class LinkStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class ReferralLink(Base):
    __tablename__ = 'referral_links'
    __table_args__ = {'schema': 'referral'} # Map to the referral schema

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    user_id = Column(UUID(as_uuid=True), ForeignKey('referral.users.id', ondelete='RESTRICT'), nullable=False) # Foreign key referencing referral.users
    unique_code = Column(Text, nullable=False, unique=True)
    click_count = Column(Integer, nullable=False, server_default='0')
    conversion_count = Column(Integer, nullable=False, server_default='0')
    status = Column(Enum(LinkStatus, name='link_status'), nullable=False, server_default=LinkStatus.ACTIVE.value)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # Relationships (uncomment and refine once related models are confirmed to exist)
    user = relationship("User", back_populates="referral_links")
    referrals = relationship("Referral", back_populates="referral_link")
