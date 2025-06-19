from sqlalchemy import Column, Text, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base

import enum

class InvitationStatus(enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"

class Invitation(Base):
    __tablename__ = 'invitations'
    __table_args__ = {'schema': 'referral'} # Map to the referral schema

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    email = Column(Text, nullable=False)
    token = Column(Text, nullable=False, unique=True)
    status = Column(Enum(InvitationStatus, name='invitation_status', create_type=False), nullable=False, server_default=InvitationStatus.PENDING.value)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # No significant relationships defined in TDD for Invitation
