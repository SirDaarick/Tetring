"""Pruebas para el dashboard académico y sincronización con el SAES.

Todas las pruebas usan la base de datos en memoria y mockean las llamadas a
`saes-api` para no depender de un servicio externo.
"""

from datetime import datetime, timezone
from unittest.mock import patch
from uuid import uuid4

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import encrypt_saes_credentials
from app.models.curriculum_course import CurriculumCourse
from app.models.current_schedule import CurrentSchedule
from app.models.kardex_entry import KardexEntry
from app.models.saes_credential import SaesCredential
from app.models.user import User


def _create_saes_credential(user: User, school: str = "escom") -> SaesCredential:
    """Crea una credencial SAES cifrada para un usuario de prueba."""
    encrypted_login, encrypted_session = encrypt_saes_credentials(
        "login-token", "session-token"
    )
    return SaesCredential(
        id=uuid4(),
        user_id=user.id,
        boleta="1234567890",
        school=school,
        encrypted_login=encrypted_login,
        encrypted_session=encrypted_session,
        saes_expires_at=datetime.now(timezone.utc),
    )


class _MockAsyncClient:
    """Cliente HTTP mínimo para mockear respuestas de `httpx.AsyncClient`."""

    def __init__(self, response_data: object) -> None:
        self._response_data = response_data

    async def __aenter__(self) -> "_MockAsyncClient":
        return self

    async def __aexit__(self, *args: object) -> bool:
        return False

    async def get(self, *args: object, **kwargs: object) -> "_MockAsyncClient":
        return self

    async def post(self, *args: object, **kwargs: object) -> "_MockAsyncClient":
        return self

    @property
    def status_code(self) -> int:
        return 200

    def json(self) -> object:
        return self._response_data


@pytest.mark.asyncio
async def test_summary_requires_auth(async_client: AsyncClient) -> None:
    """GET /dashboard/summary debe exigir autenticación."""
    response = await async_client.get("/api/v1/dashboard/summary")

    assert response.status_code == 401


@pytest.mark.asyncio
async def test_kardex_returns_entries(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """GET /dashboard/kardex debe retornar las entradas almacenadas."""
    entries = [
        KardexEntry(
            user_id=test_user.id,
            clave="A1",
            asignatura="Materia 1",
            calificacion="10",
            periodo="2025-1",
        ),
        KardexEntry(
            user_id=test_user.id,
            clave="A2",
            asignatura="Materia 2",
            calificacion="9",
            periodo="2025-1",
        ),
    ]
    db_session.add_all(entries)
    await db_session.commit()

    response = await async_client.get(
        "/api/v1/dashboard/kardex", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 2
    assert data[0]["clave"] == "A1"
    assert data[1]["clave"] == "A2"


@pytest.mark.asyncio
async def test_pending_calculates_correctly(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """GET /dashboard/pending debe mostrar solo las materias no cursadas."""
    kardex = KardexEntry(
        user_id=test_user.id,
        clave="A1",
        asignatura="Materia 1",
        calificacion="10",
        periodo="2025-1",
    )
    db_session.add(kardex)

    curriculum = [
        CurriculumCourse(
            user_id=test_user.id,
            school="escom",
            carrera="ISC",
            periodo="2025-1",
            clave="A1",
            nombre="Materia 1",
            creditos="10",
        ),
        CurriculumCourse(
            user_id=test_user.id,
            school="escom",
            carrera="ISC",
            periodo="2025-2",
            clave="A2",
            nombre="Materia 2",
            creditos="8",
        ),
    ]
    db_session.add_all(curriculum)
    await db_session.commit()

    response = await async_client.get(
        "/api/v1/dashboard/pending", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["clave"] == "A2"
    assert data[0]["periodo_curricular"] == "2025-2"


@pytest.mark.asyncio
async def test_sync_triggers_all_fetches(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """POST /dashboard/sync debe llamar a los 3 endpoints del SAES y guardar datos."""
    credential = _create_saes_credential(test_user)
    db_session.add(credential)
    await db_session.commit()

    kardex_data = [
        {
            "clave": "K1",
            "asignatura": "Kardex 1",
            "calificacion": "10",
            "periodo": "2025-1",
            "fecha": "2025-01-15",
            "formaEvaluacion": "ORD",
        }
    ]
    curriculum_data = [
        {
            "carrera": "ISC",
            "periodo": "2025-1",
            "clave": "K1",
            "nombre": "Kardex 1",
            "tipo": "Obligatoria",
            "creditos": "10",
            "horasTeoria": "3",
            "horasPractica": "2",
        }
    ]
    schedule_data = [
        {
            "grupo": "1CM1",
            "clave": "K1",
            "asignatura": "Kardex 1",
            "profesor": "Profesor A",
            "horas": {"lunes": "07:00-08:30"},
        }
    ]

    responses = [kardex_data, curriculum_data, schedule_data]

    def _mock_client(*args: object, **kwargs: object) -> _MockAsyncClient:
        return _MockAsyncClient(responses.pop(0))

    with patch("httpx.AsyncClient", new=_mock_client):
        response = await async_client.post(
            "/api/v1/dashboard/sync", headers=auth_headers
        )

    assert response.status_code == 200
    data = response.json()
    assert data["kardex"] == 1
    assert data["curriculum"] == 1
    assert data["horario"] == 1


@pytest.mark.asyncio
async def test_summary_calculates_gpa(
    async_client: AsyncClient,
    db_session: AsyncSession,
    test_user: User,
    auth_headers: dict[str, str],
) -> None:
    """GET /dashboard/summary debe calcular correctamente promedio y créditos."""
    kardex_entries = [
        KardexEntry(
            user_id=test_user.id,
            clave="A1",
            asignatura="M1",
            calificacion="10",
            periodo="2025-1",
        ),
        KardexEntry(
            user_id=test_user.id,
            clave="A2",
            asignatura="M2",
            calificacion="8",
            periodo="2025-1",
        ),
        KardexEntry(
            user_id=test_user.id,
            clave="A3",
            asignatura="M3",
            calificacion="NP",
            periodo="2025-1",
        ),
    ]
    db_session.add_all(kardex_entries)

    curriculum = [
        CurriculumCourse(
            user_id=test_user.id,
            school="escom",
            carrera="ISC",
            periodo="2025-1",
            clave="A1",
            nombre="M1",
            creditos="10",
        ),
        CurriculumCourse(
            user_id=test_user.id,
            school="escom",
            carrera="ISC",
            periodo="2025-1",
            clave="A2",
            nombre="M2",
            creditos="8",
        ),
        CurriculumCourse(
            user_id=test_user.id,
            school="escom",
            carrera="ISC",
            periodo="2025-1",
            clave="A3",
            nombre="M3",
            creditos="6",
        ),
    ]
    db_session.add_all(curriculum)
    await db_session.commit()

    response = await async_client.get(
        "/api/v1/dashboard/summary", headers=auth_headers
    )

    assert response.status_code == 200
    data = response.json()
    assert data["total_cursadas"] == 3
    assert data["promedio_general"] == 9.0
    assert data["creditos_completados"] == 18
    assert data["materias_pendientes"] == 0
    assert data["tiene_horario_actual"] is False
    assert data["pending_by_semester"] == []
