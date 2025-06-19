from app.config import settings
from logging.config import fileConfig

# Use create_async_engine for async migrations
from sqlalchemy.ext.asyncio import create_async_engine
# Import pool for NullPool
from sqlalchemy import pool
from alembic import context

import asyncio  # Import asyncio

import os  # Import os for path manipulation
import sys  # Import sys for path manipulation

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Add the parent directory of 'app' to the sys.path
# This allows Alembic's env.py to import modules from the 'app' package
sys.path.insert(0, os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')))

# Import your application's settings and base for models
# We need to import config first to load the settings
# Import your application's settings and base for models
# We need to import config first to load the settings
from app.models.base import Base # Import Base from your models

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata # Set target_metadata to your models' metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

# Use the DATABASE_URL from your settings for the SQLAlchemy URL
# This overrides the sqlalchemy.url in alembic.ini if set,
# ensuring configuration is centralized in app.config
# Ensure this URL uses the +asyncpg driver (e.g., postgresql+asyncpg://...)
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,  # Added for better compare support
        include_schemas=True # Include schemas for autogenerate
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    """Configures context for migrations."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,  # Added for better compare support
        include_schemas=True # Include schemas for autogenerate
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async engine."""
    # create an AsyncEngine
    connectable = create_async_engine(
        config.get_main_option("sqlalchemy.url"),
        poolclass=pool.NullPool,  # Use NullPool for migrations
    )

    async with connectable.connect() as connection:  # Use async context manager
        # Run synchronous migration logic within the async connection
        await connection.run_sync(do_run_migrations)

    # Dispose the engine after use
    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    # Wrap the async function call in asyncio.run
    asyncio.run(run_migrations_online())
