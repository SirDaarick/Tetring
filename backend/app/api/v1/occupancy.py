"""Rutas de la API para monitoreo de cupos en tiempo real.

Provee endpoints para verificación puntual de cupos, streaming de
actualizaciones vía Server-Sent Events (SSE) y heartbeat de sesión activa.
La autenticación en el stream SSE se realiza mediante token en query
string o cookie porque `EventSource` no permite encabezados personalizados.
"""

import uuid
from typing import Annotated, Any

from fastapi import APIRouter, Cookie, Depends, HTTPException, Query, status
from sse_starlette.sse import EventSourceResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.occupancy import (
    HeartbeatResponse,
    OccupancyCheckResponse,
)
from app.services.occupancy_service import (
    check_schedule_occupancy,
    is_session_active,
    occupancy_event_generator,
    record_heartbeat,
    require_schedule_ownership,
)
from app.services.saes_service import get_saes_tokens_for_user

router = APIRouter(prefix="/occupancy", tags=["occupancy"])


async def _get_current_user_from_token(
    token: str | None,
    db: AsyncSession,
) -> User:
    """Valida un token JWT y retorna el usuario asociado.

    Comparte la lógica con `get_current_user` pero permite recibir el token
    desde query string o cookie para soportar `EventSource`.
    """
    from jose import JWTError

    from app.core.security import ACCESS_TOKEN_TYPE, verify_token
    from app.services.auth_service import get_user_by_email

    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere un token de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        payload: dict[str, Any] = verify_token(token, ACCESS_TOKEN_TYPE)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión expirada o token inválido",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    email: str | None = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token mal formado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user: User | None = await get_user_by_email(db, email)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_user_for_sse(
    db: Annotated[AsyncSession, Depends(get_db)],
    token: Annotated[str | None, Query()] = None,
    access_token: Annotated[str | None, Cookie()] = None,
) -> User:
    """Dependencia de autenticación para endpoints SSE."""
    return await _get_current_user_from_token(token or access_token, db)


@router.post(
    "/heartbeat",
    response_model=HeartbeatResponse,
    status_code=status.HTTP_200_OK,
    summary="Heartbeat de sesión activa",
)
async def heartbeat(
    current_user: Annotated[User, Depends(get_current_user)],
) -> HeartbeatResponse:
    """Recibe un pulso del cliente para mantener activo el sondeo de cupos."""
    record_heartbeat(current_user.id)
    return HeartbeatResponse(active=True)


@router.get(
    "/check/{schedule_id}",
    response_model=OccupancyCheckResponse,
    status_code=status.HTTP_200_OK,
    summary="Verificar cupos de un horario",
)
async def check_occupancy(
    schedule_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> OccupancyCheckResponse:
    """Retorna el estado actual de cupos para cada grupo del horario guardado."""
    await require_schedule_ownership(db, schedule_id, current_user.id)
    return await check_schedule_occupancy(db, schedule_id)


@router.get(
    "/stream/{schedule_id}",
    summary="Stream SSE de actualizaciones de cupos",
)
async def stream_occupancy(
    schedule_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user_for_sse)],
) -> EventSourceResponse:
    """Transmite actualizaciones de cupos cada 60 segundos vía SSE.

    El cliente debe enviar un heartbeat cada 30 segundos para mantener el
    sondeo activo. Si no hay heartbeat durante 2 minutos, el servidor
    detiene las consultas al SAES.
    """
    from app.models.saes_credential import SaesCredential
    from sqlalchemy import select

    await require_schedule_ownership(db, schedule_id, current_user.id)

    result = await db.execute(
        select(SaesCredential).where(SaesCredential.user_id == current_user.id)
    )
    credential: SaesCredential | None = result.scalar_one_or_none()
    if credential is None:

        async def error_stream() -> Any:
            yield {
                "event": "occupancy_error",
                "data": '{"detail": "No hay una cuenta SAES vinculada"}',
            }

        return EventSourceResponse(error_stream())

    tokens = await get_saes_tokens_for_user(db, current_user.id)

    async def event_generator() -> Any:
        try:
            async for update in occupancy_event_generator(
                db=db,
                user_id=current_user.id,
                schedule_id=schedule_id,
                school=credential.school,
                login=tokens["login"],
                session=tokens["session"],
            ):
                yield {
                    "event": "occupancy_update",
                    "data": update.model_dump_json(),
                }
        except HTTPException as exc:
            yield {
                "event": "occupancy_error",
                "data": f'{{"detail": "{exc.detail}"}}',
            }
        except Exception:
            yield {
                "event": "occupancy_error",
                "data": '{"detail": "Error inesperado en el stream de cupos"}',
            }

    return EventSourceResponse(event_generator())
