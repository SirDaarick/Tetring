"""Rutas de la API para vinculación de credenciales SAES.

Todas las respuestas y mensajes de error están en español (México). El flujo
requiere dos pasos:

1. `POST /link/start`  → obtiene captcha y almacena sesión temporal.
2. `POST /link/complete` → resuelve captcha, autentica y guarda credenciales.
"""

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_db
from app.models.user import User
from app.schemas.saes import (
    CaptchaResponse,
    SaesLinkStart,
    SaesLoginSubmit,
    SaesProfileResponse,
    SchoolResponse,
)
from app.services.saes_client import get_all_schools
from app.services.saes_service import (
    get_saes_profile,
    link_saes_complete,
    link_saes_start,
    unlink_saes,
)

router = APIRouter(prefix="/saes", tags=["saes"])


@router.get(
    "/schools",
    response_model=list[SchoolResponse],
    status_code=status.HTTP_200_OK,
    summary="Listar planteles soportados",
)
async def list_schools() -> list[SchoolResponse]:
    """Retorna los planteles disponibles para vinculación SAES."""
    return [
        SchoolResponse(id=s["id"], name=s["name"], url=s["url"])
        for s in get_all_schools()
    ]


@router.post(
    "/link/start",
    response_model=CaptchaResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar vinculación SAES",
)
async def start_link(
    data: SaesLinkStart,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> CaptchaResponse:
    """Solicita un captcha al SAES e inicia el flujo de vinculación."""
    return await link_saes_start(
        db=db,
        current_user=current_user,
        boleta=data.boleta,
        school=data.school,
    )


@router.post(
    "/link/complete",
    response_model=SaesProfileResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Completar vinculación SAES",
)
async def complete_link(
    data: SaesLoginSubmit,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SaesProfileResponse:
    """Envía la solución del captcha y las credenciales para vincular SAES."""
    return await link_saes_complete(
        db=db,
        current_user=current_user,
        password=data.password,
        captcha_solution=data.captcha_solution,
    )


@router.get(
    "/profile",
    response_model=SaesProfileResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener perfil SAES vinculado",
)
async def read_profile(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> SaesProfileResponse:
    """Retorna la información de la cuenta SAES vinculada al usuario."""
    return await get_saes_profile(db=db, current_user=current_user)


@router.delete(
    "/unlink",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Eliminar vínculo SAES",
)
async def delete_link(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_user)],
) -> None:
    """Elimina la credencial SAES vinculada al usuario autenticado."""
    await unlink_saes(db=db, current_user=current_user)
