from sqlalchemy import Column, Integer, Text, ForeignKey, DateTime, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
import uuid
import enum
from datetime import datetime

from .base import Base
from .database_utils import GUID, get_datetime_default
# Import other models for relationships - ensure these are imported correctly
# from .referral_link import ReferralLink
# from .payment import Payment
# from .earning import Earning

class UserStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"

class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'schema': 'referral'} # Map to the referral schema

    id = Column(GUID(), primary_key=True)
    full_name = Column(Text, nullable=False)
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    phone_number = Column(Text, nullable=False, unique=True) # Validation handled in Pydantic
    status = Column(Enum(UserStatus, name='user_status', create_type=False), nullable=False, server_default=UserStatus.ACTIVE.value)
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
    referral_links = relationship("ReferralLink", back_populates="user")
    payments = relationship("Payment", back_populates="user")
    earnings = relationship("Earning", back_populates="user")
