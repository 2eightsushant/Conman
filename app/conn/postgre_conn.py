from sqlalchemy.ext.asyncio import AsyncSession
from db.engine_async import AsyncSessionLocal
from typing import AsyncGenerator

from shared.logger import get_logger

logger = get_logger(__name__)

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session