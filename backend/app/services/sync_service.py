"""Servicios de sincronización académica con el SAES.

Coordina la descarga de kárdex, currícula y horario actual desde `saes-api`
utilizando las credenciales cifradas del usuario. Cada sincronización reemplaza
completamente los datos previos del usuario (full replace).
"""

from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import decrypt_saes_credentials
from app.models.curriculum_course import CurriculumCourse
from app.models.current_schedule import CurrentSchedule
from app.models.kardex_entry import KardexEntry
from app.models.saes_credential import SaesCredential
from app.models.user import User
from app.services.saes_client import make_saes_request
from app.services.saes_service import update_last_sync_at


def _to_str_or_none(value: Any) -> str | None:
    """Normaliza un valor opcional a cadena o ``None`` si está vacío."""
    if value is None or value == "":
        return None
    return str(value)


async def _get_saes_credential(
    db: AsyncSession,
    user_id: Any,
) -> SaesCredential:
    """Obtiene la credencial SAES del usuario o lanza 404 si no existe."""
    result = await db.execute(
        select(SaesCredential).where(SaesCredential.user_id == user_id)
    )
    credential: SaesCredential | None = result.scalar_one_or_none()
    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay una cuenta SAES vinculada",
        )
    return credential


async def _handle_saes_error(exc: HTTPException) -> None:
    """Traduce errores de `saes-api` a mensajes de negocio en español."""
    if exc.status_code == status.HTTP_401_UNAUTHORIZED:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Sesión SAES expirada, vincúlate nuevamente",
        ) from exc
    raise exc


async def sync_kardex(db: AsyncSession, current_user: User) -> int:
    """Sincroniza el kárdex del usuario desde `/user/kardex`.

    Elimina las entradas previas e inserta los datos más recientes. Retorna
    la cantidad de entradas almacenadas.
    """
    credential = await _get_saes_credential(db, current_user.id)
    tokens = decrypt_saes_credentials(
        credential.encrypted_login,
        credential.encrypted_session,
    )

    try:
        data: Any = await make_saes_request(
            school=credential.school,
            login_token=tokens["login"],
            session_token=tokens["session"],
            path="/user/kardex",
        )
    except HTTPException as exc:
        await _handle_saes_error(exc)
        return 0

    if not isinstance(data, list):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Formato de kárdex inválido",
        )

    await db.execute(
        delete(KardexEntry).where(KardexEntry.user_id == current_user.id)
    )

    count = 0
    for item in data:
        entry = KardexEntry(
            user_id=current_user.id,
            clave=_to_str_or_none(item.get("clave")) or "",
            asignatura=_to_str_or_none(item.get("asignatura")) or "",
            calificacion=_to_str_or_none(item.get("calificacion")) or "",
            periodo=_to_str_or_none(item.get("periodo")) or "",
            fecha=_to_str_or_none(item.get("fecha")),
            forma_evaluacion=_to_str_or_none(item.get("formaEvaluacion")),
        )
        db.add(entry)
        count += 1

    await db.commit()
    return count


async def sync_curriculum(db: AsyncSession, current_user: User) -> int:
    """Sincroniza la currícula del usuario desde `/general/asignaturas`.

    Elimina los registros previos e inserta el plan de estudios completo.
    Retorna la cantidad de asignaturas almacenadas.
    """
    credential = await _get_saes_credential(db, current_user.id)
    tokens = decrypt_saes_credentials(
        credential.encrypted_login,
        credential.encrypted_session,
    )

    try:
        data: Any = await make_saes_request(
            school=credential.school,
            login_token=tokens["login"],
            session_token=tokens["session"],
            path="/general/asignaturas",
        )
    except HTTPException as exc:
        await _handle_saes_error(exc)
        return 0

    if not isinstance(data, list):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Formato de currícula inválido",
        )

    await db.execute(
        delete(CurriculumCourse).where(
            CurriculumCourse.user_id == current_user.id
        )
    )

    count = 0
    for item in data:
        course = CurriculumCourse(
            user_id=current_user.id,
            school=credential.school,
            carrera=_to_str_or_none(item.get("carrera")) or "",
            periodo=_to_str_or_none(item.get("periodo")) or "",
            clave=_to_str_or_none(item.get("clave")) or "",
            nombre=_to_str_or_none(item.get("nombre")) or "",
            tipo=_to_str_or_none(item.get("tipo")),
            creditos=_to_str_or_none(item.get("creditos")),
            horas_teoria=_to_str_or_none(item.get("horasTeoria")),
            horas_practica=_to_str_or_none(item.get("horasPractica")),
        )
        db.add(course)
        count += 1

    await db.commit()
    return count


async def sync_current_schedule(db: AsyncSession, current_user: User) -> int:
    """Sincroniza el horario actual del usuario desde `/user/horario`.

    Elimina los registros previos e inserta los grupos inscritos en el periodo
    vigente. Retorna la cantidad de grupos almacenados.
    """
    credential = await _get_saes_credential(db, current_user.id)
    tokens = decrypt_saes_credentials(
        credential.encrypted_login,
        credential.encrypted_session,
    )

    try:
        data: Any = await make_saes_request(
            school=credential.school,
            login_token=tokens["login"],
            session_token=tokens["session"],
            path="/user/horario",
        )
    except HTTPException as exc:
        await _handle_saes_error(exc)
        return 0

    if not isinstance(data, list):
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Formato de horario inválido",
        )

    await db.execute(
        delete(CurrentSchedule).where(
            CurrentSchedule.user_id == current_user.id
        )
    )

    count = 0
    for item in data:
        horas: dict[str, Any] = item.get("horas") or {}
        schedule = CurrentSchedule(
            user_id=current_user.id,
            grupo=_to_str_or_none(item.get("grupo")) or "",
            clave=_to_str_or_none(item.get("clave")) or "",
            asignatura=_to_str_or_none(item.get("asignatura")) or "",
            profesor=_to_str_or_none(item.get("profesor")) or "",
            lunes=_to_str_or_none(horas.get("lunes")),
            martes=_to_str_or_none(horas.get("martes")),
            miercoles=_to_str_or_none(horas.get("miercoles")),
            jueves=_to_str_or_none(horas.get("jueves")),
            viernes=_to_str_or_none(horas.get("viernes")),
        )
        db.add(schedule)
        count += 1

    await db.commit()
    return count


async def sync_all(db: AsyncSession, current_user: User) -> dict[str, int]:
    """Ejecuta la sincronización completa de kárdex, currícula y horario.

    Actualiza la marca de última sincronización solo si los tres pasos
    terminaron correctamente. Retorna un diccionario con los conteos.
    """
    kardex_count = await sync_kardex(db, current_user)
    curriculum_count = await sync_curriculum(db, current_user)
    schedule_count = await sync_current_schedule(db, current_user)

    await update_last_sync_at(db, current_user.id)

    return {
        "kardex": kardex_count,
        "curriculum": curriculum_count,
        "horario": schedule_count,
    }
