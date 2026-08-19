"""Pruebas para el monitoreo de cupos y streaming SSE.

Se mockean las llamadas HTTP a `saes-api` mediante `httpx.AsyncClient` para
no depender de un servicio real durante las pruebas.
"""

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

import pytest
import pytest_asyncio
from httpx import AsyncClient
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import encrypt_saes_credentials
from app.models.option_item import OptionItem
from app.models.room_occupancy import RoomOccupancy
from app.models.saes_credential import SaesCredential
from app.models.saved_schedule import SavedSchedule
from app.models.user import User
from app.schemas.occupancy import OccupancyCheckResponse
from app.services import occupancy_service
from app.services.occupancy_service import (
    check_schedule_occupancy,
    fetch_occupancy,
    find_alternatives,
    is_session_active,
    record_heartbeat,
)


class _MockResponse:
    """Respuesta HTTP simulada para mockear `httpx`."""

    def __init__(self, json_data: dict | list, status_code: int = 200):
        self._json = json_data
        self.status_code = status_code

    def json(self) -> dict | list:
        return self._json


class _MockAsyncClient:
    """Cliente HTTP simulado que respeta el contexto asíncrono de `httpx`."""

    def __init__(self, response: _MockResponse):
        self._response = response

    async def __aenter__(self) -> "_MockAsyncClient":
        return self

    async def __aexit__(self, *args: object) -> bool:
        return False

    async def get(self, *args: object, **kwargs: object) -> _MockResponse:
        return self._response

    async def post(self, *args: object, **kwargs: object) -> _MockResponse:
        return self._response


def _mock_httpx_client(json_data: dict | list, status_code: int = 200) -> _MockAsyncClient:
    """Crea un cliente HTTP simulado con la respuesta indicada."""
    return _MockAsyncClient(_MockResponse(json_data, status_code))


@pytest_asyncio.fixture
async def test_saes_credential(db_session: AsyncSession, test_user: User) -> SaesCredential:
    """Credencial SAES de prueba con tokens cifrados válidos."""
    encrypted_login, encrypted_session = encrypt_saes_credentials(
        "login-token", "session-token"
    )
    credential = SaesCredential(
        user_id=test_user.id,
        boleta="2020010001",
        school="escom",
        encrypted_login=encrypted_login,
        encrypted_session=encrypted_session,
        saes_expires_at=datetime.now(timezone.utc) + timedelta(hours=2),
    )
    db_session.add(credential)
    await db_session.commit()
    await db_session.refresh(credential)
    return credential


@pytest_asyncio.fixture
async def test_saved_schedule(
    db_session: AsyncSession,
    test_user: User,
) -> SavedSchedule:
    """Horario guardado de prueba con dos grupos."""
    schedule = SavedSchedule(
        user_id=test_user.id,
        name="Horario de prueba",
        is_favorite=False,
    )
    db_session.add(schedule)
    await db_session.flush()
    await db_session.refresh(schedule)

    items = [
        OptionItem(
            schedule_id=schedule.id,
            grupo="1AM1",
            clave="MAT-101",
            asignatura="Matemáticas",
            profesor="Profesor A",
            order_index=0,
        ),
        OptionItem(
            schedule_id=schedule.id,
            grupo="1AF1",
            clave="FIS-101",
            asignatura="Física",
            profesor="Profesor B",
            order_index=1,
        ),
    ]
    db_session.add_all(items)
    await db_session.commit()
    await db_session.refresh(schedule)
    return schedule


@pytest.mark.asyncio
async def test_fetch_occupancy_saves_to_db(
    db_session: AsyncSession,
    test_saes_credential: SaesCredential,
) -> None:
    """`fetch_occupancy` consulta SAES y persiste los registros en la BD."""
    cupos_data = [
        {
            "carrera": "ISC",
            "grupo": "1AM1",
            "clave": "MAT-101",
            "asignatura": "Matemáticas",
            "periodo": "2026-1",
            "cupo": 30,
            "inscritos": 20,
            "disponibles": 10,
        },
        {
            "carrera": "ISC",
            "grupo": "1AF1",
            "clave": "FIS-101",
            "asignatura": "Física",
            "periodo": "2026-1",
            "cupo": 25,
            "inscritos": 22,
            "disponibles": 3,
        },
    ]

    with patch(
        "app.services.saes_client.httpx.AsyncClient",
        return_value=_mock_httpx_client(cupos_data),
    ):
        count = await fetch_occupancy(
            db_session,
            school="escom",
            login="login-token",
            session="session-token",
        )

    assert count == 2

    result = await db_session.execute(
        select(RoomOccupancy).where(RoomOccupancy.grupo == "1AM1")
    )
    record = result.scalar_one()
    assert record.disponibles == 10
    assert record.asignatura == "Matemáticas"


@pytest.mark.asyncio
async def test_check_schedule_returns_status_for_all_groups(
    db_session: AsyncSession,
    test_saved_schedule: SavedSchedule,
) -> None:
    """`check_schedule_occupancy` retorna un estado por cada grupo del horario."""
    db_session.add_all(
        [
            RoomOccupancy(
                carrera="ISC",
                grupo="1AM1",
                clave="MAT-101",
                asignatura="Matemáticas",
                periodo="2026-1",
                cupo=30,
                inscritos=20,
                disponibles=10,
            ),
            RoomOccupancy(
                carrera="ISC",
                grupo="1AF1",
                clave="FIS-101",
                asignatura="Física",
                periodo="2026-1",
                cupo=25,
                inscritos=22,
                disponibles=3,
            ),
        ]
    )
    await db_session.commit()

    response: OccupancyCheckResponse = await check_schedule_occupancy(
        db_session, test_saved_schedule.id
    )

    assert response.schedule_id == test_saved_schedule.id
    assert len(response.groups) == 2
    assert response.tiene_riesgo is True
    assert "grupo(s) tienen cupo crítico" in response.resumen


@pytest.mark.asyncio
async def test_status_disponible_when_available_10(db_session: AsyncSession) -> None:
    """Un grupo con 10 disponibles tiene estado 'disponible'."""
    db_session.add(
        RoomOccupancy(
            carrera="ISC",
            grupo="1AM1",
            clave="MAT-101",
            asignatura="Matemáticas",
            periodo="2026-1",
            cupo=30,
            inscritos=20,
            disponibles=10,
        )
    )
    await db_session.commit()

    result = await db_session.execute(
        select(RoomOccupancy).where(RoomOccupancy.grupo == "1AM1")
    )
    record = result.scalar_one()
    assert occupancy_service._determine_status(record.disponibles) == "disponible"


@pytest.mark.asyncio
async def test_status_critico_when_available_3(db_session: AsyncSession) -> None:
    """Un grupo con 3 disponibles tiene estado 'critico'."""
    db_session.add(
        RoomOccupancy(
            carrera="ISC",
            grupo="1AF1",
            clave="FIS-101",
            asignatura="Física",
            periodo="2026-1",
            cupo=25,
            inscritos=22,
            disponibles=3,
        )
    )
    await db_session.commit()

    result = await db_session.execute(
        select(RoomOccupancy).where(RoomOccupancy.grupo == "1AF1")
    )
    record = result.scalar_one()
    assert occupancy_service._determine_status(record.disponibles) == "critico"


@pytest.mark.asyncio
async def test_status_lleno_when_available_0(db_session: AsyncSession) -> None:
    """Un grupo con 0 disponibles tiene estado 'lleno'."""
    db_session.add(
        RoomOccupancy(
            carrera="ISC",
            grupo="1AL1",
            clave="LEN-101",
            asignatura="Lenguaje",
            periodo="2026-1",
            cupo=20,
            inscritos=20,
            disponibles=0,
        )
    )
    await db_session.commit()

    result = await db_session.execute(
        select(RoomOccupancy).where(RoomOccupancy.grupo == "1AL1")
    )
    record = result.scalar_one()
    assert occupancy_service._determine_status(record.disponibles) == "lleno"


@pytest.mark.asyncio
async def test_find_alternatives_returns_other_groups(
    db_session: AsyncSession,
) -> None:
    """`find_alternatives` retorna otros grupos de la misma materia con cupo."""
    db_session.add_all(
        [
            RoomOccupancy(
                carrera="ISC",
                grupo="1AM1",
                clave="MAT-101",
                asignatura="Matemáticas",
                periodo="2026-1",
                cupo=30,
                inscritos=30,
                disponibles=0,
            ),
            RoomOccupancy(
                carrera="ISC",
                grupo="1AM2",
                clave="MAT-101",
                asignatura="Matemáticas",
                periodo="2026-1",
                cupo=30,
                inscritos=20,
                disponibles=10,
            ),
            RoomOccupancy(
                carrera="ISC",
                grupo="1AM3",
                clave="MAT-101",
                asignatura="Matemáticas",
                periodo="2026-1",
                cupo=30,
                inscritos=27,
                disponibles=3,
            ),
        ]
    )
    await db_session.commit()

    alternatives = await find_alternatives(db_session, grupo="1AM1", clave="MAT-101")

    assert len(alternatives) == 2
    groups = {alt.grupo for alt in alternatives}
    assert groups == {"1AM2", "1AM3"}
    assert alternatives[0].grupo == "1AM2"  # Mayor disponibilidad primero


@pytest.mark.asyncio
async def test_heartbeat_returns_active(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    test_user: User,
) -> None:
    """El endpoint de heartbeat confirma la sesión activa."""
    response = await async_client.post(
        "/api/v1/occupancy/heartbeat",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["active"] is True
    assert is_session_active(test_user.id) is True


@pytest.mark.asyncio
async def test_check_endpoint_returns_occupancy(
    async_client: AsyncClient,
    auth_headers: dict[str, str],
    test_saved_schedule: SavedSchedule,
    db_session: AsyncSession,
) -> None:
    """El endpoint GET /check/{schedule_id} retorna el estado de cupos."""
    db_session.add(
        RoomOccupancy(
            carrera="ISC",
            grupo="1AM1",
            clave="MAT-101",
            asignatura="Matemáticas",
            periodo="2026-1",
            cupo=30,
            inscritos=20,
            disponibles=10,
        )
    )
    await db_session.commit()

    response = await async_client.get(
        f"/api/v1/occupancy/check/{test_saved_schedule.id}",
        headers=auth_headers,
    )
    assert response.status_code == 200
    data = response.json()
    assert data["schedule_id"] == str(test_saved_schedule.id)
    assert len(data["groups"]) == 2
    assert data["tiene_riesgo"] is False
    assert "Todos los grupos" in data["resumen"]


@pytest.mark.asyncio
async def test_heartbeat_cleans_inactive_sessions(test_user: User) -> None:
    """Las sesiones inactivas se detectan correctamente tras el timeout."""
    record_heartbeat(test_user.id)
    assert is_session_active(test_user.id) is True

    # Simular una sesión expirada modificando el timestamp interno.
    occupancy_service._active_sessions[test_user.id] = (
        datetime.now(timezone.utc) - timedelta(minutes=5)
    )
    assert is_session_active(test_user.id) is False
