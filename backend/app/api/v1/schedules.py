"""Rutas de la API para generación y guardado de horarios.

Expone endpoints para generar horarios sin empalmes, guardar favoritos,
listar horarios guardados, alternar el estado de favorito y eliminar
horarios. Todos los endpoints requieren autenticación.
"""

import uuid
from typing import Annotated

from fastapi import APIRouter, Depends, Response, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.schedule import (
    GenerateRequest,
    GenerateResponse,
    SaveScheduleRequest,
    SavedScheduleResponse,
    OptionItemResponse,
)
from app.services import schedule_service

router = APIRouter(prefix="/schedules", tags=["schedules"])


@router.post(
    "/generate",
    response_model=GenerateResponse,
    status_code=status.HTTP_200_OK,
    summary="Generar horarios",
)
async def generate(
    request: GenerateRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> GenerateResponse:
    """Genera horarios válidos sin empalmes para las materias seleccionadas."""
    return await schedule_service.generate(
        db=db,
        current_user=current_user,
        request=request,
    )


@router.get(
    "/professors",
    response_model=list[str],
    status_code=status.HTTP_200_OK,
    summary="Listar profesores para materias pendientes",
)
async def list_professors(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[str]:
    """Retorna una lista de profesores distintos de los grupos disponibles para las materias pendientes."""
    return await schedule_service.get_professors(
        db=db,
        current_user=current_user,
    )


@router.get(
    "/groups",
    response_model=list[OptionItemResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar todos los grupos disponibles para las materias pendientes",
)
async def list_available_groups(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[OptionItemResponse]:
    """Retorna la lista de todos los grupos ofertados en SAES para las materias pendientes."""
    return await schedule_service.get_available_groups(
        db=db,
        current_user=current_user,
    )


@router.post(
    "/save",
    response_model=SavedScheduleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Guardar horario",
)
async def save(
    request: SaveScheduleRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SavedScheduleResponse:
    """Guarda un horario generado como favorito del usuario."""
    return await schedule_service.save_schedule(
        db=db,
        current_user=current_user,
        request=request,
    )


@router.get(
    "/saved",
    response_model=list[SavedScheduleResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar horarios guardados",
)
async def list_saved(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> list[SavedScheduleResponse]:
    """Retorna todos los horarios guardados del usuario."""
    return await schedule_service.get_saved_schedules(
        db=db,
        current_user=current_user,
    )


@router.put(
    "/saved/{schedule_id}/favorite",
    response_model=SavedScheduleResponse,
    status_code=status.HTTP_200_OK,
    summary="Alternar favorito",
)
async def favorite(
    schedule_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SavedScheduleResponse:
    """Alterna el estado de favorito de un horario guardado."""
    return await schedule_service.toggle_favorite(
        db=db,
        current_user=current_user,
        schedule_id=schedule_id,
    )


@router.delete(
    "/saved/{schedule_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar horario guardado",
)
async def delete(
    schedule_id: uuid.UUID,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> Response:
    """Elimina un horario guardado del usuario."""
    await schedule_service.delete_saved_schedule(
        db=db,
        current_user=current_user,
        schedule_id=schedule_id,
    )
    return Response(status_code=status.HTTP_204_NO_CONTENT)
