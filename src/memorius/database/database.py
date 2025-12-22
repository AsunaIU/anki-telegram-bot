from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from memorius.config import settings
from memorius.database.models import Base

engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_pre_ping=True)

async_session_maker = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def get_session() -> AsyncSession:
    """Get database session"""
    async with async_session_maker() as session:
        yield session
