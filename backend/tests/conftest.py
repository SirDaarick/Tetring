"""Configuración y fixtures para pruebas asíncronas del backend.

Provee un cliente HTTP asíncrono basado en `httpx` que apunta directamente
a la aplicación FastAPI sin levantar un servidor real.
"""

from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


@pytest.fixture
async def async_client() -> AsyncGenerator[AsyncClient, None]:
    """Cliente asíncrono para pruebas de integración con FastAPI."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        yield client
