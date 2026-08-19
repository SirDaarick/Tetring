"""Servicios de negocio para monitoreo de cupos.

Coordina la consulta de cupos al SAES, la persistencia temporal de la
ocupación, el cálculo de estados de disponibilidad y la búsqueda de
grupos alternativos. También rastrea sesiones activas mediante heartbeats
en memoria para decidir cuándo detener el sondeo al SAES.
"""

import asyncio
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.option_item import OptionItem
from app.models.room_occupancy import RoomOccupancy
from app.models.saved_schedule import SavedSchedule
from app.schemas.occupancy import (
    OccupancyCheckResponse,
    OccupancyResponse,
)
from app.services.saes_client import make_saes_request

# Sesiones de usuario activas para sondeo de cupos.
# user_id -> timestamp del último heartbeat.
_active_sessions: dict[uuid.UUID, datetime] = {}
_HEARTBEAT_TIMEOUT: timedelta = timedelta(minutes=2)
_POLL_INTERVAL_SECONDS: int = 60


def _determine_status(disponibles: int) -> str:
    """Calcula el estado de disponibilidad a partir de los lugares libres."""
    if disponibles >= 10:
        return "disponible"
    if disponibles >= 5:
        return "bajo"
    if disponibles >= 1:
        return "critico"
    return "lleno"


def _build_response(occupancy: RoomOccupancy) -> OccupancyResponse:
    """Construye el esquema de respuesta a partir de un modelo de ocupación."""
    return OccupancyResponse(
        grupo=occupancy.grupo,
        clave=occupancy.clave,
        asignatura=occupancy.asignatura,
        cupo=occupancy.cupo,
        inscritos=occupancy.inscritos,
        disponibles=occupancy.disponibles,
        fetched_at=occupancy.fetched_at,
        status=_determine_status(occupancy.disponibles),
    )


def _build_unknown_response(grupo: str, clave: str, asignatura: str) -> OccupancyResponse:
    """Construye una respuesta para un grupo sin registro de ocupación."""
    return OccupancyResponse(
        grupo=grupo,
        clave=clave,
        asignatura=asignatura,
        cupo=0,
        inscritos=0,
        disponibles=0,
        fetched_at=datetime.now(timezone.utc),
        status="desconocido",
    )


def _extract_cupos_list(raw: Any) -> list[dict[str, Any]]:
    """Normaliza la respuesta de `/general/cupos` a una lista de registros."""
    if isinstance(raw, list):
        return raw
    if isinstance(raw, dict):
        for key in ("cupos", "data", "groups", "grupos"):
            value = raw.get(key)
            if isinstance(value, list):
                return value
    return []


async def _upsert_occupancy_record(
    db: AsyncSession,
    record: dict[str, Any],
    fetched_at: datetime,
) -> None:
    """Inserta o actualiza un registro de ocupación en la base de datos."""
    carrera = str(record.get("carrera", ""))
    grupo = str(record.get("grupo", ""))
    clave = str(record.get("clave", ""))
    if not (carrera and grupo and clave):
        return

    result = await db.execute(
        select(RoomOccupancy).where(
            RoomOccupancy.carrera == carrera,
            RoomOccupancy.grupo == grupo,
            RoomOccupancy.clave == clave,
        )
    )
    existing: RoomOccupancy | None = result.scalar_one_or_none()

    if existing is not None:
        existing.asignatura = str(record.get("asignatura", existing.asignatura))
        existing.periodo = str(record.get("periodo", existing.periodo))
        existing.cupo = int(record.get("cupo", existing.cupo))
        existing.inscritos = int(record.get("inscritos", existing.inscritos))
        existing.disponibles = int(record.get("disponibles", existing.disponibles))
        existing.fetched_at = fetched_at
    else:
        db.add(
            RoomOccupancy(
                carrera=carrera,
                grupo=grupo,
                clave=clave,
                asignatura=str(record.get("asignatura", "")),
                periodo=str(record.get("periodo", "")),
                cupo=int(record.get("cupo", 0)),
                inscritos=int(record.get("inscritos", 0)),
                disponibles=int(record.get("disponibles", 0)),
                fetched_at=fetched_at,
            )
        )


async def fetch_occupancy(
    db: AsyncSession,
    school: str,
    login: str,
    session: str,
) -> int:
    """Consulta `/general/cupos` en SAES y actualiza la tabla `room_occupancy`.

    Retorna la cantidad de registros procesados.
    """
    raw = await make_saes_request(
        school=school,
        login_token=login,
        session_token=session,
        path="/general/cupos",
        method="GET",
    )

    records = _extract_cupos_list(raw)
    fetched_at = datetime.now(timezone.utc)

    for record in records:
        await _upsert_occupancy_record(db, record, fetched_at)

    if records:
        await db.commit()

    return len(records)


async def check_schedule_occupancy(
    db: AsyncSession,
    schedule_id: uuid.UUID,
) -> OccupancyCheckResponse:
    """Retorna el estado de cupos para todos los grupos de un horario guardado."""
    result = await db.execute(
        select(OptionItem).where(OptionItem.schedule_id == schedule_id)
    )
    items: list[OptionItem] = list(result.scalars().all())

    groups: list[OccupancyResponse] = []
    risk_count = 0

    for item in items:
        occupancy_result = await db.execute(
            select(RoomOccupancy)
            .where(
                RoomOccupancy.grupo == item.grupo,
                RoomOccupancy.clave == item.clave,
            )
            .order_by(RoomOccupancy.fetched_at.desc())
            .limit(1)
        )
        occupancy: RoomOccupancy | None = occupancy_result.scalar_one_or_none()

        if occupancy is not None:
            response = _build_response(occupancy)
        else:
            response = _build_unknown_response(item.grupo, item.clave, item.asignatura)

        if response.status in ("critico", "lleno"):
            risk_count += 1

        groups.append(response)

    if risk_count == 0:
        resumen = "Todos los grupos tienen cupo disponible"
    else:
        resumen = f"{risk_count} grupo(s) tienen cupo crítico o están llenos"

    return OccupancyCheckResponse(
        schedule_id=schedule_id,
        groups=groups,
        tiene_riesgo=risk_count > 0,
        resumen=resumen,
    )


async def find_alternatives(
    db: AsyncSession,
    grupo: str,
    clave: str,
) -> list[OccupancyResponse]:
    """Busca otros grupos de la misma asignatura que aún tengan cupo."""
    result = await db.execute(
        select(RoomOccupancy)
        .where(
            RoomOccupancy.clave == clave,
            RoomOccupancy.grupo != grupo,
            RoomOccupancy.disponibles > 0,
        )
        .order_by(RoomOccupancy.disponibles.desc())
    )
    records = result.scalars().all()
    return [_build_response(record) for record in records]


def record_heartbeat(user_id: uuid.UUID) -> None:
    """Marca una sesión de usuario como activa para sondeo de cupos."""
    _active_sessions[user_id] = datetime.now(timezone.utc)


def is_session_active(user_id: uuid.UUID) -> bool:
    """Indica si la sesión de un usuario sigue activa según sus heartbeats."""
    last = _active_sessions.get(user_id)
    if last is None:
        return False
    return datetime.now(timezone.utc) - last < _HEARTBEAT_TIMEOUT


def clean_inactive_sessions() -> None:
    """Elimina sesiones que no han enviado heartbeat en el tiempo límite."""
    now = datetime.now(timezone.utc)
    expired = [
        user_id
        for user_id, last in _active_sessions.items()
        if now - last >= _HEARTBEAT_TIMEOUT
    ]
    for user_id in expired:
        _active_sessions.pop(user_id, None)


async def occupancy_event_generator(
    db: AsyncSession,
    user_id: uuid.UUID,
    schedule_id: uuid.UUID,
    school: str,
    login: str,
    session: str,
) -> Any:
    """Generador asíncrono que emite actualizaciones de cupos cada 60 segundos.

    Detiene el sondeo cuando la sesión deja de estar activa o el cliente
    cierra la conexión.
    """
    record_heartbeat(user_id)

    try:
        while True:
            if not is_session_active(user_id):
                break

            await fetch_occupancy(db, school, login, session)
            yield await check_schedule_occupancy(db, schedule_id)

            await asyncio.sleep(_POLL_INTERVAL_SECONDS)
    except asyncio.CancelledError:
        raise


async def verify_schedule_ownership(
    db: AsyncSession,
    schedule_id: uuid.UUID,
    user_id: uuid.UUID,
) -> bool:
    """Verifica que un horario guardado pertenezca al usuario indicado."""
    result = await db.execute(
        select(SavedSchedule).where(
            SavedSchedule.id == schedule_id,
            SavedSchedule.user_id == user_id,
        )
    )
    return result.scalar_one_or_none() is not None


async def require_schedule_ownership(
    db: AsyncSession,
    schedule_id: uuid.UUID,
    user_id: uuid.UUID,
) -> None:
    """Lanza 404 si el horario no existe o no pertenece al usuario."""
    if not await verify_schedule_ownership(db, schedule_id, user_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Horario no encontrado",
        )


class OccupancyService:
    """Fachada de servicio para monitoreo de cupos.

    Expone los métodos de negocio como una clase para facilitar la
    inyección de dependencias y la verificación de importación.
    """

    @staticmethod
    async def fetch_occupancy(
        db: AsyncSession,
        school: str,
        login: str,
        session: str,
    ) -> int:
        """Consulta `/general/cupos` y actualiza `room_occupancy`."""
        return await fetch_occupancy(db, school, login, session)

    @staticmethod
    async def check_schedule_occupancy(
        db: AsyncSession,
        schedule_id: uuid.UUID,
    ) -> OccupancyCheckResponse:
        """Retorna el estado de cupos para un horario guardado."""
        return await check_schedule_occupancy(db, schedule_id)

    @staticmethod
    async def find_alternatives(
        db: AsyncSession,
        grupo: str,
        clave: str,
    ) -> list[OccupancyResponse]:
        """Busca otros grupos de la misma asignatura con disponibilidad."""
        return await find_alternatives(db, grupo, clave)
