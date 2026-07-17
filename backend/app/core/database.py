"""Configuración de SQLAlchemy asíncrono para SQLite (desarrollo) y PostgreSQL (producción).

El motor y la fábrica de sesiones se crean a partir de `DATABASE_URL`.
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.core.config import settings

engine = create_async_engine(
    settings.DATABASE_URL,
    echo=False,
    future=True,
)

AsyncSessionLocal: async_sessionmaker[AsyncSession] = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)

Base = declarative_base()


async def get_db_session() -> AsyncSession:
    """Fábrica de sesiones para inyección de dependencias."""
    async with AsyncSessionLocal() as session:
        yield session
