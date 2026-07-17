"""Servicios de autenticación para usuarios locales y OAuth de Google.

Contiene la lógica de negocio para registro, inicio de sesión, generación de
JWT y vinculación de cuentas de Google, con mensajes de error en español.
"""

from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

from fastapi import HTTPException, status
from jose import JWTError
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.security import (
    ACCESS_TOKEN_TYPE,
    REFRESH_TOKEN_TYPE,
    create_access_token,
    create_refresh_token,
    get_password_hash,
    verify_password,
    verify_token,
)
from app.models.user import User
from app.schemas.auth import TokenResponse, UserCreate, UserLogin


async def get_user_by_email(db: AsyncSession, email: str) -> User | None:
    """Busca un usuario por su correo electrónico."""
    result = await db.execute(select(User).where(User.email == email))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    """Busca un usuario por su identificador único."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def get_user_by_google_id(db: AsyncSession, google_id: str) -> User | None:
    """Busca un usuario vinculado a una cuenta de Google."""
    result = await db.execute(select(User).where(User.google_id == google_id))
    return result.scalar_one_or_none()


async def register_user(db: AsyncSession, user_data: UserCreate) -> User:
    """Registra un nuevo usuario con correo y contraseña hasheada.

    Lanza 409 si el correo ya está registrado.
    """
    existing_user = await get_user_by_email(db, user_data.email)
    if existing_user is not None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Este correo ya está registrado",
        )

    user = User(
        email=user_data.email,
        password_hash=get_password_hash(user_data.password),
        full_name=user_data.full_name,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def authenticate_user(db: AsyncSession, credentials: UserLogin) -> User:
    """Verifica correo y contraseña, devolviendo el usuario si son válidos.

    Lanza 401 si las credenciales son incorrectas o si la cuenta no tiene
    contraseña (cuenta de Google pura).
    """
    user = await get_user_by_email(db, credentials.email)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if user.password_hash is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Esta cuenta usa inicio de sesión con Google",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not verify_password(credentials.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def create_tokens(user: User) -> TokenResponse:
    """Genera un par de tokens JWT (acceso y refresco) para un usuario."""
    extra_claims: dict[str, Any] = {
        "email": user.email,
        "full_name": user.full_name,
    }
    access_token = create_access_token(subject=user.email, extra_claims=extra_claims)
    refresh_token = create_refresh_token(subject=user.email)
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
    )


async def refresh_access_token(db: AsyncSession, refresh_token: str) -> TokenResponse:
    """Valida un refresh token y emite un nuevo par de tokens.

    Lanza 401 si el token es inválido, expiró o si el usuario no existe.
    """
    try:
        payload: dict[str, Any] = verify_token(refresh_token, REFRESH_TOKEN_TYPE)
    except JWTError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida, inicia sesión nuevamente",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc

    email: str | None = payload.get("sub")
    if email is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de refresco mal formado",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user_by_email(db, email)
    if user is None or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión inválida, inicia sesión nuevamente",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return create_tokens(user)


async def get_or_create_google_user(
    db: AsyncSession,
    google_id: str,
    email: str,
    full_name: str | None,
) -> User:
    """Obtiene un usuario existente de Google o crea uno nuevo.

    Si existe un usuario con el mismo correo pero sin `google_id`, se vincula
    la cuenta de Google a ese usuario (flujo de vinculación).
    """
    user_by_google = await get_user_by_google_id(db, google_id)
    if user_by_google is not None:
        return user_by_google

    user_by_email = await get_user_by_email(db, email)
    if user_by_email is not None:
        user_by_email.google_id = google_id
        if full_name and not user_by_email.full_name:
            user_by_email.full_name = full_name
        await db.commit()
        await db.refresh(user_by_email)
        return user_by_email

    new_user = User(
        email=email,
        google_id=google_id,
        full_name=full_name,
        password_hash=None,
    )
    db.add(new_user)
    try:
        await db.commit()
    except IntegrityError as exc:
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="No se pudo crear la cuenta de Google; el correo ya existe",
        ) from exc
    await db.refresh(new_user)
    return new_user
