import pytest
import asyncio
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool
from fastapi import FastAPI

from app.main import app
from app.core.database import Base, get_db
from app.config import settings
import os

# Import all models to ensure they're registered with Base.metadata
from app.models.invitation import Invitation
from app.models.user import User
from app.models.referral_link import ReferralLink
from app.models.admin_user import AdminUser
from app.models.earning import Earning
from app.models.payment import Payment
from app.models.referral import Referral

# Test database URL - use SQLite for tests to avoid external dependencies
TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

# Create test engine and session
test_engine = create_async_engine(
    TEST_DATABASE_URL,
    poolclass=NullPool,
)
TestingSessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=test_engine,
    class_=AsyncSession,
)

@pytest.fixture(scope="session")
def event_loop():
    """Create an instance of the default event loop for each test case."""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

def remove_schema_from_metadata(metadata):
    """Remove schema from all tables in metadata for SQLite compatibility."""
    for table in metadata.tables.values():
        table.schema = None

@pytest.fixture(scope="session")
async def setup_database():
    """Set up the test database once for the test session."""
    # For SQLite, we need to remove schema references from table metadata
    # This is a workaround for testing with SQLite
    remove_schema_from_metadata(Base.metadata)
    
    # Create all tables
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    yield
    
    # Drop all tables after tests
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    
    # Clean up test database file
    if os.path.exists("./test.db"):
        os.remove("./test.db")

@pytest.fixture
async def test_db(setup_database):
    """Create a fresh database session for each test."""
    async with TestingSessionLocal() as session:
        try:
            yield session
        finally:
            # Clean up all data after each test
            for table in reversed(Base.metadata.sorted_tables):
                await session.execute(table.delete())
            await session.commit()
            await session.close()

@pytest.fixture
async def async_session(setup_database):
    """Create a fresh database session for each test (alias for test_db)."""
    async with TestingSessionLocal() as session:
        yield session
        # Roll back any changes made during the test
        await session.rollback()

@pytest.fixture
async def client(test_db):
    """Create a test client with the test database."""
    # Override the get_db dependency to use the test database
    async def override_get_db():
        try:
            yield test_db
        finally:
            await test_db.close()
    
    app.dependency_overrides[get_db] = override_get_db
    
    # Create and return the test client
    async with AsyncClient(app=app, base_url="http://test") as client:
        yield client
    
    # Clear dependency overrides after test
    app.dependency_overrides.clear()