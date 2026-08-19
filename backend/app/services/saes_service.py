"""Servicios de negocio para la vinculación de credenciales SAES.

Coordina la comunicación con `saes-api`, el cifrado de credenciales y el
almacenamiento en base de datos. Los mensajes de error están en español.
"""

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decrypt_saes_credentials, encrypt_saes_credentials
from app.models.saes_credential import SaesCredential
from app.models.user import User
from app.schemas.saes import CaptchaResponse, SaesProfileResponse
from app.services.saes_client import authenticate_saes, get_saes_session


@dataclass
class _LinkSession:
    """Datos temporales de una sesión de vinculación en curso."""

    credential: str
    captcha_id: str
    boleta: str
    school: str
    created_at: datetime


# Almacenamiento temporal en memoria para sesiones de captcha. En producción
# debería reemplazarse por Redis con TTL.
_link_sessions: dict[uuid.UUID, _LinkSession] = {}
_LINK_SESSION_TTL: timedelta = timedelta(minutes=10)


def _clean_expired_sessions() -> None:
    """Elimina sesiones de vinculación que ya excedieron su TTL."""
    now: datetime = datetime.now(timezone.utc)
    expired: list[uuid.UUID] = [
        user_id
        for user_id, session in _link_sessions.items()
        if now - session.created_at > _LINK_SESSION_TTL
    ]
    for user_id in expired:
        _link_sessions.pop(user_id, None)


def _get_cached_session(user_id: uuid.UUID) -> _LinkSession:
    """Obtiene la sesión de vinculación en caché o lanza 400 si no existe."""
    _clean_expired_sessions()
    session: _LinkSession | None = _link_sessions.get(user_id)
    if session is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No hay una sesión de vinculación activa; solicita un captcha primero",
        )
    return session


async def _get_credential_by_boleta(
    db: AsyncSession, boleta: str
) -> SaesCredential | None:
    """Busca una credencial SAES existente por boleta."""
    result = await db.execute(
        select(SaesCredential).where(SaesCredential.boleta == boleta)
    )
    return result.scalar_one_or_none()


async def _get_credential_by_user(
    db: AsyncSession, user_id: uuid.UUID
) -> SaesCredential | None:
    """Busca una credencial SAES existente por usuario."""
    result = await db.execute(
        select(SaesCredential).where(SaesCredential.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def link_saes_start(
    db: AsyncSession,
    current_user: User,
    boleta: str,
    school: str,
) -> CaptchaResponse:
    """Inicia el flujo de vinculación SAES solicitando un captcha.

    Valida que la boleta no esté vinculada a otra cuenta, solicita una
    sesión de captcha a `saes-api` y almacena los datos temporalmente en
    memoria hasta que el usuario resuelva el captcha.
    """
    existing: SaesCredential | None = await _get_credential_by_boleta(db, boleta)
    if existing is not None and existing.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Esta boleta ya está vinculada a otra cuenta",
        )

    try:
        session_data: dict[str, Any] = await get_saes_session(school)
    except HTTPException:
        raise

    credential: str = session_data.get("credential", "")
    captcha: dict[str, Any] = session_data.get("captcha", {})
    captcha_id: str = captcha.get("id", "")
    captcha_base64: str = captcha.get("imageBase64", "")

    if not credential or not captcha_id:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="SAES no devolvió datos de captcha válidos",
        )

    _link_sessions[current_user.id] = _LinkSession(
        credential=credential,
        captcha_id=captcha_id,
        boleta=boleta,
        school=school,
        created_at=datetime.now(timezone.utc),
    )

    return CaptchaResponse(
        credential=credential,
        captcha_id=captcha_id,
        captcha_base64=captcha_base64,
    )


async def link_saes_complete(
    db: AsyncSession,
    current_user: User,
    password: str,
    captcha_solution: str,
) -> SaesProfileResponse:
    """Completa la vinculación SAES tras resolver el captcha.

    Recupera la sesión temporal, autentica al usuario en `saes-api`, cifra
    los tokens `login` y `session`, y los almacena en la base de datos.
    """
    session: _LinkSession = _get_cached_session(current_user.id)

    try:
        auth_data: dict[str, Any] = await authenticate_saes(
            school=session.school,
            credential=session.credential,
            username=session.boleta,
            password=password,
            captcha_id=session.captcha_id,
            captcha_solution=captcha_solution,
        )
    except HTTPException:
        raise

    credentials_data = auth_data.get("credentials", {})
    login_token: str = credentials_data.get("login", "") or auth_data.get("login", "")
    session_token: str = credentials_data.get("session", "") or auth_data.get("session", "")
    if not login_token or not session_token:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="SAES no devolvió credenciales completas",
        )

    update_after: int | None = auth_data.get("updateAfter")
    expires_at: datetime
    if update_after is not None:
        expires_at = datetime.fromtimestamp(update_after / 1000, tz=timezone.utc)
    else:
        expires_at = datetime.now(timezone.utc) + timedelta(hours=2)

    encrypted_login, encrypted_session = encrypt_saes_credentials(
        login_token, session_token
    )

    # Si el usuario ya tenía una credencial, la actualizamos.
    credential: SaesCredential | None = await _get_credential_by_user(
        db, current_user.id
    )
    now: datetime = datetime.now(timezone.utc)
    if credential is None:
        credential = SaesCredential(
            user_id=current_user.id,
            boleta=session.boleta,
            school=session.school,
            encrypted_login=encrypted_login,
            encrypted_session=encrypted_session,
            saes_expires_at=expires_at,
            created_at=now,
            updated_at=now,
        )
        db.add(credential)
    else:
        credential.boleta = session.boleta
        credential.school = session.school
        credential.encrypted_login = encrypted_login
        credential.encrypted_session = encrypted_session
        credential.saes_expires_at = expires_at
        credential.updated_at = now

    await db.commit()
    await db.refresh(credential)

    # Limpia la sesión temporal para evitar reutilización.
    _link_sessions.pop(current_user.id, None)

    return SaesProfileResponse(
        boleta=credential.boleta,
        school=credential.school,
        linked_at=credential.created_at,
        last_sync_at=credential.last_sync_at,
    )


async def get_saes_profile(
    db: AsyncSession,
    current_user: User,
) -> SaesProfileResponse:
    """Retorna el perfil de la cuenta SAES vinculada al usuario actual."""
    credential: SaesCredential | None = await _get_credential_by_user(
        db, current_user.id
    )
    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay una cuenta SAES vinculada",
        )

    return SaesProfileResponse(
        boleta=credential.boleta,
        school=credential.school,
        linked_at=credential.created_at,
        last_sync_at=credential.last_sync_at,
    )


async def unlink_saes(db: AsyncSession, current_user: User) -> None:
    """Elimina la credencial SAES vinculada al usuario actual."""
    credential: SaesCredential | None = await _get_credential_by_user(
        db, current_user.id
    )
    if credential is not None:
        await db.delete(credential)
        await db.commit()
    _link_sessions.pop(current_user.id, None)


async def get_saes_tokens_for_user(
    db: AsyncSession, user_id: uuid.UUID
) -> dict[str, str]:
    """Descifra y retorna los tokens SAES de un usuario.

    Utilizado por otros servicios (sincronización académica, cupos) que
    necesitan llamar a `saes-api` en nombre del usuario.
    """
    result = await db.execute(
        select(SaesCredential).where(SaesCredential.user_id == user_id)
    )
    credential: SaesCredential | None = result.scalar_one_or_none()
    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay una cuenta SAES vinculada",
        )

    return decrypt_saes_credentials(
        credential.encrypted_login,
        credential.encrypted_session,
    )


async def update_last_sync_at(
    db: AsyncSession, user_id: uuid.UUID, sync_at: datetime | None = None
) -> None:
    """Actualiza la marca de tiempo de la última sincronización académica."""
    result = await db.execute(
        select(SaesCredential).where(SaesCredential.user_id == user_id)
    )
    credential: SaesCredential | None = result.scalar_one_or_none()
    if credential is None:
        return

    credential.last_sync_at = sync_at or datetime.now(timezone.utc)
    credential.updated_at = datetime.now(timezone.utc)
    await db.commit()
