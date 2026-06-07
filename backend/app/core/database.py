from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.core.config import settings

from sqlalchemy import NullPool
import uuid

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    poolclass=NullPool,
    connect_args={
        "statement_cache_size": 0,
        "prepared_statement_name_func": lambda: f"__asyncpg_{uuid.uuid4().hex}__",
    },  # Required for Supabase transaction pooler (PgBouncer)
)
async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    """Base class for all SQLAlchemy ORM models."""
    pass


async def init_db():
    """Create all tables in Supabase PostgreSQL on startup."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("[OK] Supabase PostgreSQL tables initialized.")


async def close_db():
    """Dispose the engine on shutdown."""
    await engine.dispose()
    print("[INFO] Database connection closed.")


async def get_db() -> AsyncSession:
    """Dependency: yield a database session per request."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()
