"""Pruebas para el módulo de vinculación de credenciales SAES.

Todas las pruebas usan mocks para evitar llamadas reales a `saes-api`.
"""

from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decrypt_saes_credentials, encrypt_saes_credentials
from app.models.saes_credential import SaesCredential
from app.models.user import User
from app.services.saes_client import get_all_schools


@pytest.mark.asyncio
async def test_get_schools_returns_escom_and_esiatec(
    async_client: AsyncClient,
) -> None:
    """GET /saes/schools debe retornar ESCOM y ESIATEC."""
    response = await async_client.get("/api/v1/saes/schools")

    assert response.status_code == 200
    schools = response.json()
    assert len(schools) == 2
    assert schools[0]["id"] == "escom"
    assert schools[1]["id"] == "esiatec"


@pytest.mark.asyncio
async def test_link_start_requires_auth(async_client: AsyncClient) -> None:
    """POST /saes/link/start debe exigir autenticación."""
    response = await async_client.post(
        "/api/v1/saes/link/start",
        json={"boleta": "1234567890", "school": "escom"},
    )

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_link_start_duplicate_boleta_returns_409(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict[str, str],
    test_user_2: User,
    auth_headers_user_2: dict[str, str],
) -> None:
    """Una boleta ya vinculada a otro usuario debe rechazarse con 409."""
    boleta: str = "1234567890"

    # Vinculamos la boleta al primer usuario directamente en base de datos.
    encrypted_login, encrypted_session = encrypt_saes_credentials("login", "session")
    credential = SaesCredential(
        id=uuid4(),
        user_id=test_user.id,
        boleta=boleta,
        school="escom",
        encrypted_login=encrypted_login,
        encrypted_session=encrypted_session,
        saes_expires_at=datetime.now(timezone.utc),
    )
    db_session.add(credential)
    await db_session.commit()

    # El segundo usuario intenta iniciar vinculación con la misma boleta.
    mocked_session = {
        "credential": "cred-123",
        "captcha": {"id": "captcha-123", "imageBase64": "base64data"},
    }
    with patch(
        "app.services.saes_service.get_saes_session", new=AsyncMock(return_value=mocked_session)
    ):
        response = await async_client.post(
            "/api/v1/saes/link/start",
            headers=auth_headers_user_2,
            json={"boleta": boleta, "school": "escom"},
        )

    assert response.status_code == 409
    assert "boleta" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_link_complete_requires_cached_session(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
) -> None:
    """POST /saes/link/complete sin sesión temporal previa debe retornar 400."""
    response = await async_client.post(
        "/api/v1/saes/link/complete",
        headers=auth_headers,
        json={"password": "secret", "captcha_solution": "ABCD"},
    )

    assert response.status_code == 400


@pytest.mark.asyncio
async def test_unlink_removes_credentials(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """DELETE /saes/unlink debe eliminar la credencial SAES del usuario."""
    encrypted_login, encrypted_session = encrypt_saes_credentials("login", "session")
    credential = SaesCredential(
        id=uuid4(),
        user_id=test_user.id,
        boleta="1234567890",
        school="escom",
        encrypted_login=encrypted_login,
        encrypted_session=encrypted_session,
        saes_expires_at=datetime.now(timezone.utc),
    )
    db_session.add(credential)
    await db_session.commit()

    response = await async_client.delete(
        "/api/v1/saes/unlink",
        headers=auth_headers,
    )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_get_profile_returns_linked_account(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """GET /saes/profile debe retornar la cuenta SAES vinculada."""
    encrypted_login, encrypted_session = encrypt_saes_credentials("login", "session")
    linked_at = datetime.now(timezone.utc)
    credential = SaesCredential(
        id=uuid4(),
        user_id=test_user.id,
        boleta="1234567890",
        school="escom",
        encrypted_login=encrypted_login,
        encrypted_session=encrypted_session,
        saes_expires_at=linked_at,
        created_at=linked_at,
    )
    db_session.add(credential)
    await db_session.commit()

    response = await async_client.get(
        "/api/v1/saes/profile",
        headers=auth_headers,
    )

    assert response.status_code == 200
    profile = response.json()
    assert profile["boleta"] == "1234567890"
    assert profile["school"] == "escom"
    assert profile["linked_at"] is not None


@pytest.mark.asyncio
async def test_link_complete_success(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """Flujo completo de vinculación: start → complete → perfil."""
    boleta: str = "1234567890"
    school: str = "escom"

    mocked_session = {
        "credential": "cred-123",
        "captcha": {"id": "captcha-123", "imageBase64": "base64img"},
    }
    mocked_auth = {
        "login": "saes-login-token",
        "session": "saes-session-token",
        "updateAfter": int(datetime.now(timezone.utc).timestamp() * 1000) + 7200000,
    }

    with patch(
        "app.services.saes_service.get_saes_session", new=AsyncMock(return_value=mocked_session)
    ), patch(
        "app.services.saes_service.authenticate_saes", new=AsyncMock(return_value=mocked_auth)
    ):
        start_response = await async_client.post(
            "/api/v1/saes/link/start",
            headers=auth_headers,
            json={"boleta": boleta, "school": school},
        )
        assert start_response.status_code == 200
        captcha = start_response.json()
        assert captcha["credential"] == "cred-123"
        assert captcha["captcha_id"] == "captcha-123"

        complete_response = await async_client.post(
            "/api/v1/saes/link/complete",
            headers=auth_headers,
            json={"password": "secret", "captcha_solution": "ABCD"},
        )
        assert complete_response.status_code == 201
        profile = complete_response.json()
        assert profile["boleta"] == boleta
        assert profile["school"] == school

    # Verifica que los tokens se almacenaron cifrados, nunca en texto plano.
    result = await db_session.execute(
        select(SaesCredential).where(SaesCredential.user_id == test_user.id)
    )
    stored: SaesCredential | None = result.scalar_one_or_none()
    assert stored is not None
    assert b"saes-login-token" not in stored.encrypted_login
    assert b"saes-session-token" not in stored.encrypted_session

    decrypted = decrypt_saes_credentials(stored.encrypted_login, stored.encrypted_session)
    assert decrypted["login"] == "saes-login-token"
    assert decrypted["session"] == "saes-session-token"


@pytest.mark.asyncio
async def test_get_all_schools_function() -> None:
    """El cliente SAES debe exponer ESCOM y ESIATEC."""
    schools = get_all_schools()
    assert len(schools) == 2
    assert schools[0]["id"] == "escom"
    assert schools[1]["id"] == "esiatec"
    assert "Escuela Superior de Cómputo" in schools[0]["name"]
