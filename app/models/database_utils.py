"""
Database utilities for cross-database compatibility.
Handles differences between PostgreSQL and SQLite.
"""
from sqlalchemy import String, DateTime, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from sqlalchemy.types import TypeDecorator, CHAR
import uuid


class GUID(TypeDecorator):
    """
    Platform-independent GUID type.
    Uses PostgreSQL's UUID type when available, otherwise uses CHAR(36).
    """
    impl = CHAR
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == 'postgresql':
            return dialect.type_descriptor(UUID(as_uuid=True))
        else:
            return dialect.type_descriptor(CHAR(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        elif dialect.name == 'postgresql':
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return str(value)
            else:
                return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        else:
            if not isinstance(value, uuid.UUID):
                return uuid.UUID(value)
            return value


def get_uuid_default(dialect_name=None):
    """
    Get appropriate UUID default for the database dialect.
    """
    # For PostgreSQL, use gen_random_uuid()
    # For SQLite and others, we'll handle this in Python code
    if dialect_name == 'postgresql':
        return func.gen_random_uuid()
    else:
        # For SQLite, we'll need to handle UUID generation in Python
        # This will be None and we'll generate UUIDs in the application
        return None


def get_datetime_default():
    """
    Get appropriate datetime default for the database dialect.
    For SQLite, we'll use text('CURRENT_TIMESTAMP').
    For PostgreSQL, we'll use func.now().
    Since we can't determine dialect at definition time, we'll use a generic approach.
    """
    # Use text for cross-database compatibility
    return text('CURRENT_TIMESTAMP')


# Database-agnostic column definitions
def uuid_column(primary_key=False, foreign_key=None, nullable=True):
    """Create a UUID column that works across databases."""
    kwargs = {
        'type_': GUID(),
        'primary_key': primary_key,
        'nullable': nullable
    }
    
    # Only add server_default for primary keys in PostgreSQL
    # For other cases, we'll generate UUIDs in Python
    if primary_key:
        # We'll handle this in the model's __init__ method for SQLite
        pass
    
    if foreign_key:
        kwargs['foreign_key'] = foreign_key
    
    return kwargs


def datetime_column(nullable=False, default=True):
    """Create a datetime column that works across databases."""
    kwargs = {
        'type_': DateTime(timezone=True),
        'nullable': nullable
    }
    
    if default:
        # Use database-specific default
        kwargs['server_default'] = get_datetime_default()
    
    return kwargs