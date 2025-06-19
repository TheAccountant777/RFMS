"""create_initial_schema

Revision ID: 8ee7f667f606
Revises:
Create Date: 2025-06-19 12:01:30.232925

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, ENUM
from sqlalchemy.sql import func

# revision identifiers, used by Alembic.
revision: str = '8ee7f667f606'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Explicitly create the referral schema if it doesn't exist
    op.execute("CREATE SCHEMA IF NOT EXISTS referral;")

    # Grant permissions on the schema to the database user
    # Replace 'your_db_user' with the actual user from your DATABASE_URL
    op.execute("GRANT CREATE ON SCHEMA referral TO \"postgres.spsxkfjihzytmatdyhuh\";")
    op.execute("GRANT USAGE ON SCHEMA referral TO \"postgres.spsxkfjihzytmatdyhuh\";")


    # Create ENUM types
    op.execute("CREATE TYPE user_status AS ENUM ('ACTIVE', 'INACTIVE');")
    op.execute("CREATE TYPE invitation_status AS ENUM ('PENDING', 'ACCEPTED', 'EXPIRED');")
    op.execute("CREATE TYPE link_status AS ENUM ('ACTIVE', 'INACTIVE');")
    op.execute("CREATE TYPE referral_status AS ENUM ('PENDING', 'SIGNED_UP', 'CONVERTED');")
    op.execute("CREATE TYPE earning_status AS ENUM ('SCHEDULED', 'PENDING_APPROVAL', 'PAID', 'FAILED');")
    op.execute("CREATE TYPE payment_status AS ENUM ('PENDING_DISBURSEMENT', 'PROCESSING', 'SUCCESS', 'FAILED');")
    op.execute("CREATE TYPE admin_role AS ENUM ('CTO', 'CEO', 'FINANCE');")

    # Create tables using raw SQL via op.execute()
    op.execute("""
        CREATE TABLE referral.users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            full_name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            phone_number TEXT UNIQUE NOT NULL,
            status user_status NOT NULL DEFAULT 'ACTIVE',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE referral.admin_users (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role admin_role NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE referral.invitations (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            email TEXT NOT NULL,
            token TEXT UNIQUE NOT NULL,
            status invitation_status NOT NULL DEFAULT 'PENDING',
            expires_at TIMESTAMPTZ NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE referral.referral_links (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            user_id UUID NOT NULL REFERENCES referral.users(id) ON DELETE RESTRICT,
            unique_code TEXT UNIQUE NOT NULL,
            click_count INTEGER NOT NULL DEFAULT 0,
            conversion_count INTEGER NOT NULL DEFAULT 0,
            status link_status NOT NULL DEFAULT 'ACTIVE',
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE referral.referrals (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            referral_link_id UUID NOT NULL REFERENCES referral.referral_links(id) ON DELETE CASCADE,
            referred_user_id TEXT,
            status referral_status NOT NULL DEFAULT 'PENDING',
            earnings_paid_count INTEGER NOT NULL DEFAULT 0,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            signed_up_at TIMESTAMPTZ,
            converted_at TIMESTAMPTZ,
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE referral.payments (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            batch_id UUID NOT NULL,
            user_id UUID NOT NULL REFERENCES referral.users(id) ON DELETE RESTRICT,
            total_amount NUMERIC(10, 2) NOT NULL,
            mpesa_transaction_id TEXT UNIQUE,
            status payment_status NOT NULL DEFAULT 'PENDING_DISBURSEMENT',
            processed_at TIMESTAMPTZ,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)

    op.execute("""
        CREATE TABLE referral.earnings (
            id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
            referral_id UUID NOT NULL REFERENCES referral.referrals(id) ON DELETE CASCADE,
            user_id UUID NOT NULL REFERENCES referral.users(id) ON DELETE RESTRICT,
            payment_id UUID REFERENCES referral.payments(id) ON DELETE SET NULL,
            amount NUMERIC(10, 2) NOT NULL DEFAULT 50.00,
            status earning_status NOT NULL DEFAULT 'SCHEDULED',
            due_date DATE NOT NULL,
            created_at TIMESTAMPTZ NOT NULL DEFAULT now(),
            updated_at TIMESTAMPTZ NOT NULL DEFAULT now()
        );
    """)


    # Create indexes
    op.create_index('idx_referral_links_user_id', 'referral_links', ['user_id'], schema='referral')
    op.create_index('idx_referrals_referral_link_id', 'referrals', ['referral_link_id'], schema='referral')
    op.create_index('idx_referrals_referred_user_id', 'referrals', ['referred_user_id'], schema='referral')
    op.create_index('idx_payments_user_id', 'payments', ['user_id'], schema='referral')
    op.create_index('idx_payments_batch_id', 'payments', ['batch_id'], schema='referral')
    op.create_index('idx_earnings_referral_id', 'earnings', ['referral_id'], schema='referral')
    op.create_index('idx_earnings_user_id', 'earnings', ['user_id'], schema='referral')
    op.create_index('idx_earnings_payment_id', 'earnings', ['payment_id'], schema='referral')
    op.create_index('idx_earnings_status_due_date', 'earnings', ['status', 'due_date'], schema='referral')


def downgrade() -> None:
    """Downgrade schema."""
    # Drop tables using raw SQL via op.execute()
    op.execute("DROP TABLE referral.earnings;")
    op.execute("DROP TABLE referral.payments;")
    op.execute("DROP TABLE referral.referrals;")
    op.execute("DROP TABLE referral.referral_links;")
    op.execute("DROP TABLE referral.invitations;")
    op.execute("DROP TABLE referral.admin_users;")
    op.execute("DROP TABLE referral.users;")

    # Drop ENUM types
    op.execute("DROP TYPE admin_role;")
    op.execute("DROP TYPE payment_status;")
    op.execute("DROP TYPE earning_status;")
    op.execute("DROP TYPE referral_status;")
    op.execute("DROP TYPE link_status;")
    op.execute("DROP TYPE invitation_status;")
    op.execute("DROP TYPE user_status;")

    # Drop the referral schema
    op.execute("DROP SCHEMA referral CASCADE;") # Use CASCADE to drop dependent objects
