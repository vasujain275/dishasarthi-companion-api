from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import settings

# Create async database engine with proper configuration
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
    # Add proper pool settings for async
    pool_pre_ping=True,
    pool_recycle=3600,
    connect_args={"server_settings": {"timezone": "UTC"}},
)

# Create async session factory with proper configuration
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession, autoflush=False
)

# Base class for declarative models
Base = declarative_base()


# Dependency to get async DB session
async def get_db():
    session = AsyncSessionLocal()
    try:
        yield session
    finally:
        await session.close()
