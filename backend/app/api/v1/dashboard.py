"""Rutas de la API para el dashboard académico del usuario.

Expone endpoints para consultar el resumen, kárdex, materias pendientes,
horario actual y para disparar una sincronización completa con el SAES.
Todos los endpoints requieren autenticación.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.dashboard import (
    CurrentScheduleResponse,
    DashboardSummaryResponse,
    KardexEntryResponse,
    PendingSubjectResponse,
    SyncResultResponse,
)
from app.services.dashboard_service import (
    get_current_schedule,
    get_kardex,
    get_pending,
    get_summary,
)
from app.services.sync_service import sync_all

router = APIRouter(prefix="/dashboard", tags=["dashboard"])


@router.get(
    "/summary",
    response_model=DashboardSummaryResponse,
    status_code=status.HTTP_200_OK,
    summary="Resumen académico del usuario",
)
async def summary(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> DashboardSummaryResponse:
    """Retorna el resumen consolidado del dashboard académico."""
    return await get_summary(db=db, current_user=current_user)


@router.get(
    "/kardex",
    response_model=list[KardexEntryResponse],
    status_code=status.HTTP_200_OK,
    summary="Kárdex del usuario",
)
async def kardex(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[KardexEntryResponse]:
    """Retorna las entradas del kárdex sincronizadas."""
    return await get_kardex(db=db, current_user=current_user)


@router.get(
    "/pending",
    response_model=list[PendingSubjectResponse],
    status_code=status.HTTP_200_OK,
    summary="Materias pendientes",
)
async def pending(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[PendingSubjectResponse]:
    """Retorna las materias de la currícula que aún no están en el kárdex."""
    return await get_pending(db=db, current_user=current_user)


@router.get(
    "/schedule",
    response_model=list[CurrentScheduleResponse],
    status_code=status.HTTP_200_OK,
    summary="Horario actual",
)
async def schedule(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[CurrentScheduleResponse]:
    """Retorna los grupos inscritos en el horario actual."""
    return await get_current_schedule(db=db, current_user=current_user)


@router.post(
    "/sync",
    response_model=SyncResultResponse,
    status_code=status.HTTP_200_OK,
    summary="Sincronizar datos académicos",
)
async def sync(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SyncResultResponse:
    """Sincroniza kárdex, currícula y horario actual con el SAES.

    Requiere que el usuario tenga una cuenta SAES vinculada.
    """
    counts = await sync_all(db=db, current_user=current_user)
    return SyncResultResponse(**counts)
