from sqlalchemy import Column, Text, Enum, DateTime
from sqlalchemy.sql import func
import uuid
import enum
from datetime import datetime

from .base import Base
from .database_utils import GUID, get_datetime_default

class InvitationStatus(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"

class Invitation(Base):
    __tablename__ = 'invitations'
    __table_args__ = {'schema': 'referral'} # Map to the referral schema

    id = Column(GUID(), primary_key=True)
    email = Column(Text, nullable=False)
    token = Column(Text, nullable=False, unique=True)
    status = Column(Enum(InvitationStatus, name='invitation_status', create_type=False), nullable=False, server_default=InvitationStatus.PENDING.value)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=get_datetime_default())

    def __init__(self, **kwargs):
        # Generate UUID if not provided (for SQLite compatibility)
        if 'id' not in kwargs:
            kwargs['id'] = uuid.uuid4()
        if 'created_at' not in kwargs:
            kwargs['created_at'] = datetime.utcnow()
        super().__init__(**kwargs)

    # No significant relationships defined in TDD for Invitation
