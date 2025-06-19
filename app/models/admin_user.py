from sqlalchemy import Column, Text, Enum, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func

from .base import Base

import enum

class AdminRole(enum.Enum):
    CTO = "CTO"
    CEO = "CEO"
    FINANCE = "FINANCE"

class AdminUser(Base):
    __tablename__ = 'admin_users'
    __table_args__ = {'schema': 'referral'} # Map to the referral schema

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    email = Column(Text, nullable=False, unique=True)
    password_hash = Column(Text, nullable=False)
    role = Column(Enum(AdminRole, name='admin_role', create_type=False), nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    updated_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    # No significant relationships defined in TDD for AdminUser
