import asyncpg
from fastapi import Request
from app.config import POSTGRECONFIG as PG
from app.shared.logger import get_logger

logger = get_logger(__name__)

DATABASE_URL = f'postgresql://{PG.USER}:{PG.PASS}@{PG.HOST}:{PG.PORT}/{PG.DB}'

async def connect_db():
    logger.info("Creating connection to Postgres...")
    return await asyncpg.create_pool(DATABASE_URL)

def get_db_pool(request: Request) -> asyncpg.Pool:
    try:
        return request.app.state.db_pool
    except Exception as e:
        logger.error("Cannot get DB Pool")
        raise