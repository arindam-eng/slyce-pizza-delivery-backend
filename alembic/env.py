import asyncio
from logging.config import fileConfig

from sqlalchemy.pool import NullPool
from sqlalchemy.ext.asyncio import create_async_engine, AsyncConnection
from alembic import context

from app.database import Base
from app.config import settings  # Ensure DATABASE_URL is defined here

# Alembic Config object, which provides access to the .ini file
config = context.config

# Set up logging
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# MetaData for 'autogenerate' support
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url") or settings.DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: AsyncConnection):
    """Run migrations synchronously within an async connection."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online() -> None:
    """Run migrations in 'online' mode with async support."""
    connectable = create_async_engine(settings.DATABASE_URL, poolclass=NullPool)

    async with connectable.begin() as connection:
        await connection.run_sync(do_run_migrations)  # ✅ Calls do_run_migrations synchronously

    await connectable.dispose()


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())  # ✅ Ensures proper execution of async function
