from logging.config import fileConfig

from sqlalchemy.ext.asyncio import async_engine_from_config
from sqlalchemy import pool
import asyncio

from alembic import context
from app.config.settings import settings

from app.db.base import Base
from app.db.models import *
from app.db.models.user import User
from app.db.models.chatmessage import ChatMessage
from app.db.models.chatsession import ChatSession

from app.shared.logger import get_logger

logger = get_logger("alembic.runtime.migration")

config = context.config

fileConfig(config.config_file_name)

DATABASE_URL = settings.database.database_url
config.set_main_option("sqlalchemy.url", DATABASE_URL)

logger.info(f"Url: {DATABASE_URL}")
target_metadata = Base.metadata


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    logger.info(f"Tables in metadata: {Base.metadata.tables.keys()}")
    context.configure(
        url=DATABASE_URL,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda conn: context.configure(
                connection=conn, 
                target_metadata=target_metadata, 
                compare_type=True,
                transaction_per_migration=True
            )
        )

        await connection.run_sync(lambda _: context.run_migrations())
    

def run():
    if context.is_offline_mode():
        run_migrations_offline()
    else:
        asyncio.run(run_migrations_online())

run()