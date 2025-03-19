from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base

from app.config import settings

# Create async database engine
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=True,
)

# Create async session factory - using async_sessionmaker
AsyncSessionLocal = async_sessionmaker(
    engine, expire_on_commit=False, class_=AsyncSession, autoflush=False
)

# Base class for declarative models
Base = declarative_base()


# Dependency to get async DB session
async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()
