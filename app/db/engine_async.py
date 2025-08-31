from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.config.settings import settings

DATABASE_URL = settings.database.database_url

engine = create_async_engine(
    DATABASE_URL,
    echo=False,
    pool_size=10,         # tune based on workload
    max_overflow=20,      # allow temporary bursts
    pool_timeout=30,      # seconds to wait for a connection
    pool_recycle=1800,
)
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    expire_on_commit=False,
    class_=AsyncSession,
)