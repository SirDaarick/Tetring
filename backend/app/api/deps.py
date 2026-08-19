"""Dependencias reutilizables para la API.

Provee la sesión de base de datos asíncrona y la extracción del usuario
actual a partir del token JWT enviado en el encabezado Authorization.
"""

from typing import Annotated, AsyncGenerator

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import AsyncSessionLocal
from app.core.security import ACCESS_TOKEN_TYPE, verify_token
from app.models.user import User
from app.services.auth_service import get_user_by_email


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependencia que entrega una sesión de base de datos asíncrona."""
    async with AsyncSessionLocal() as session:
        yield session


security_scheme = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security_scheme)],
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Extrae y valida el token JWT del encabezado Authorization: Bearer.

    Lanza 401 si el token falta, está expirado, tiene tipo incorrecto o si
    el usuario asociado no existe o está desactivado.
    """
    if credentials is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Se requiere un token de autenticación",
            headers={"WWW-Authenticate": "Bearer"},
        )

    token: str = credentials.credentials
    try:
        payload: dict = verify_token(token, ACCESS_TOKEN_TYPE)
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
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario no encontrado",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Cuenta desactivada",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user
