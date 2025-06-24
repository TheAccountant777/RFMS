from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base
from typing import AsyncGenerator

from app.config import settings

# Create an asynchronous database engine
# Use the database_url from settings
engine = create_async_engine(settings.database_url, echo=True) # Set echo=True for SQL logging (useful for debugging)

# Create a configured "Session" class
async_session = async_sessionmaker(
    engine,
    expire_on_commit=False, # Keep objects in session after commit
    class_=AsyncSession # Use AsyncSession
)

# Define a base class for declarative models
Base = declarative_base()

# Dependency for FastAPI to get a database session
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency that provides an async database session."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()

# Note: The actual table definitions are in app/models/ and linked via Base.metadata