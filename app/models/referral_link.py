from sqlalchemy import Column, Integer, Text, ForeignKey, Enum, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from datetime import datetime

from .base import Base
from .database_utils import GUID, get_datetime_default
# Import other models for relationships - ensure these are imported correctly
# from .user import User # Import User for ForeignKey
# from .referral import Referral # Import Referral for relationship

class LinkStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class ReferralLink(Base):
    __tablename__ = 'referral_links'
    __table_args__ = {'schema': 'referral'} # Map to the referral schema

    id = Column(GUID(), primary_key=True)
    user_id = Column(GUID(), ForeignKey('referral.users.id', ondelete='RESTRICT'), nullable=False) # Foreign key referencing referral.users
    unique_code = Column(Text, nullable=False, unique=True)
    click_count = Column(Integer, nullable=False, server_default='0')
    conversion_count = Column(Integer, nullable=False, server_default='0')
    status = Column(Enum(LinkStatus, name='link_status', create_type=False), nullable=False, server_default=LinkStatus.ACTIVE.value)
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

    # Relationships (uncomment and refine once related models are confirmed to exist)
    user = relationship("User", back_populates="referral_links")
    referrals = relationship("Referral", back_populates="referral_link")
