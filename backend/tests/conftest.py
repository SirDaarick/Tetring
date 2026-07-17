"""Configuración y fixtures para pruebas asíncronas del backend.

Provee un cliente HTTP asíncrono basado en `httpx` que apunta directamente
a la aplicación FastAPI sin levantar un servidor real. Además crea una base
de datos SQLite en memoria para cada test y permite inyectar un usuario de
prueba autenticado.
"""

from collections.abc import AsyncGenerator
from datetime import datetime, timezone

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.api.deps import get_db
from app.core.database import Base
from app.main import app
from app.models.user import User
from app.services.auth_service import create_tokens

TEST_DATABASE_URL: str = "sqlite+aiosqlite:///:memory:"


test_engine = create_async_engine(TEST_DATABASE_URL, future=True, echo=False)
TestSessionLocal = async_sessionmaker(
    test_engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
    autocommit=False,
)


@pytest_asyncio.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Sesión de base de datos asíncrona aislada en memoria para cada test."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture
async def async_client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Cliente asíncrono para pruebas de integración con FastAPI.

    Sustituye la dependencia `get_db` para usar la sesión de prueba.
    """
    async def _override_get_db() -> AsyncGenerator[AsyncSession, None]:
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client

    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def test_user(db_session: AsyncSession) -> User:
    """Crea un usuario de prueba autenticado por correo y contraseña."""
    user = User(
        email="test@example.com",
        password_hash=None,
        full_name="Usuario de Prueba",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers(test_user: User) -> dict[str, str]:
    """Genera encabezados de autorización para el usuario de prueba."""
    tokens = create_tokens(test_user)
    return {"Authorization": f"Bearer {tokens.access_token}"}


@pytest_asyncio.fixture
async def test_user_2(db_session: AsyncSession) -> User:
    """Crea un segundo usuario de prueba para escenarios de conflicto."""
    user = User(
        email="test2@example.com",
        password_hash=None,
        full_name="Segundo Usuario",
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest_asyncio.fixture
async def auth_headers_user_2(test_user_2: User) -> dict[str, str]:
    """Genera encabezados de autorización para el segundo usuario de prueba."""
    tokens = create_tokens(test_user_2)
    return {"Authorization": f"Bearer {tokens.access_token}"}
