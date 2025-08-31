from sqlalchemy.ext.asyncio import AsyncSession
from app.db.engine_async import AsyncSessionLocal
from contextlib import asynccontextmanager
from typing import AsyncGenerator

@asynccontextmanager
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()