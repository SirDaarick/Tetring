"""Servicios de negocio para generación y guardado de horarios.

Coordina la consulta de materias pendientes, la obtención de grupos
 disponibles desde SAES, la ejecución del algoritmo de backtracking y la
 persistencia de horarios favoritos.
"""

import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.algorithms.scheduler import (
    GroupSlot,
    ScoredSchedule,
    SubjectWithGroups,
    generate_schedules,
    parse_week_schedule,
)
from app.models.option_item import OptionItem
from app.models.saved_schedule import SavedSchedule
from app.models.user import User
from app.schemas.schedule import (
    GenerateRequest,
    GenerateResponse,
    OptionItemResponse,
    SaveScheduleRequest,
    SavedScheduleResponse,
    ScheduleResultResponse,
)
from app.services.dashboard_service import get_pending
from app.services.saes_client import make_saes_request
from app.services.saes_service import get_saes_tokens_for_user


async def _get_credential_for_user(
    db: AsyncSession,
    user_id: uuid.UUID,
) -> Any:
    """Obtiene la credencial SAES vinculada al usuario."""
    from app.models.saes_credential import SaesCredential

    result = await db.execute(
        select(SaesCredential).where(SaesCredential.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def _infer_user_career(db: AsyncSession, user_id: uuid.UUID) -> str | None:
    """Infiere la carrera del usuario a partir de su kárdex y currícula, mapeando al nombre de SAES."""
    from app.models.kardex_entry import KardexEntry
    from app.models.curriculum_course import CurriculumCourse

    kardex_result = await db.execute(
        select(KardexEntry.clave).where(KardexEntry.user_id == user_id)
    )
    kardex_claves = {row[0].strip().upper() for row in kardex_result.all() if row[0]}
    if not kardex_claves:
        return None

    curriculum_result = await db.execute(
        select(CurriculumCourse).where(CurriculumCourse.user_id == user_id)
    )
    curriculum_courses = list(curriculum_result.scalars().all())

    from collections import Counter
    carreras_detectadas = []
    for course in curriculum_courses:
        if course.clave.strip().upper() in kardex_claves and course.carrera and course.carrera != 'B':
            carreras_detectadas.append(course.carrera)

    carrera_codigo = None
    if carreras_detectadas:
        carrera_codigo = Counter(carreras_detectadas).most_common(1)[0][0]
    else:
        for course in curriculum_courses:
            if course.carrera and course.carrera != 'B':
                carrera_codigo = course.carrera
                break

    from app.models.saes_credential import SaesCredential
    saes_result = await db.execute(
        select(SaesCredential).where(SaesCredential.user_id == user_id)
    )
    saes_credential = saes_result.scalar_one_or_none()
    school = (saes_credential.school if saes_credential else "").lower()

    if school == "esiatec":
        mapeo = {
            'A': 'INGENIERO ARQUITECTO',
            'C': 'INGENIERO CIVIL',
            'ARQ': 'INGENIERO ARQUITECTO',
            'IC': 'INGENIERO CIVIL',
        }
    else:
        mapeo = {
            'S': 'SISTEMAS COMPUTACIONALES',
            'C': 'CIENCIA DE DATOS',
            'A': 'INTELIGENCIA ARTIFICIAL',
        }
    return mapeo.get(carrera_codigo, carrera_codigo)


async def _fetch_subject_groups(
    school: str,
    tokens: dict[str, str],
    claves: list[str],
    carrera: str | None = None,
) -> list[dict[str, Any]]:
    """Consulta los grupos disponibles en SAES para una lista de claves."""
    try:
        params = {"claves": ",".join(claves)}
        if carrera:
            params["carrera"] = carrera
        
        print(f"[schedule_service] Fetching groups for school={school}, carrera={carrera}, claves_count={len(claves)}")
        
        data = await make_saes_request(
            school=school,
            login_token=tokens["login"],
            session_token=tokens["session"],
            path="/general/horarios",
            method="GET",
            params=params,
        )
        
        print(f"[schedule_service] Success. Received data type: {type(data)}")
        
    except HTTPException as exc:
        print(f"[schedule_service] HTTPException in fetch_groups: status={exc.status_code}, detail={exc.detail}")
        raise
    except Exception as exc:
        print(f"[schedule_service] Unexpected error in fetch_groups: {str(exc)}")
        import traceback
        traceback.print_exc()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=f"SAES no disponible, intenta más tarde (error: {str(exc)})",
        ) from exc

    if isinstance(data, list):
        return data
    if isinstance(data, dict):
        for key in ("grupos", "data", "groups", "horarios"):
            if key in data and isinstance(data[key], list):
                return data[key]
    return []


def _build_subjects_with_groups(
    pending_subjects: list[Any],
    raw_groups: list[dict[str, Any]],
) -> list[SubjectWithGroups]:
    """Construye las materias con sus opciones de grupo a partir de datos crudos."""
    import re
    
    def normalizar(texto: str) -> str:
        if not texto:
            return ""
        texto = texto.upper().strip()
        replacements = (
            ("Á", "A"), ("É", "E"), ("Í", "I"), ("Ó", "O"), ("Ú", "U"),
            ("Ä", "A"), ("Ë", "E"), ("Ï", "I"), ("Ö", "O"), ("Ü", "U")
        )
        for a, b in replacements:
            texto = texto.replace(a, b)
        texto = re.sub(r'[^A-Z0-9]', '', texto)
        return texto

    clave_by_nombre_norm: dict[str, str] = {}
    for pending in pending_subjects:
        nombre_norm = normalizar(pending.nombre)
        if nombre_norm:
            clave_by_nombre_norm[nombre_norm] = pending.clave

    groups_by_clave: dict[str, list[dict[str, Any]]] = {}
    for raw in raw_groups:
        clave = raw.get("clave") or raw.get("materia") or raw.get("asignatura_clave")
        if not clave:
            asignatura = raw.get("asignatura")
            if asignatura:
                asignatura_norm = normalizar(asignatura)
                clave = clave_by_nombre_norm.get(asignatura_norm)

        if clave:
            groups_by_clave.setdefault(str(clave), []).append(raw)

    subjects: list[SubjectWithGroups] = []
    for pending in pending_subjects:
        clave = pending.clave
        raw_for_subject = groups_by_clave.get(clave, [])
        groups: list[GroupSlot] = []
        for raw in raw_for_subject:
            horas = raw.get("horas") or {}
            lunes = raw.get("lunes") or horas.get("lunes")
            martes = raw.get("martes") or horas.get("martes")
            miercoles = raw.get("miercoles") or horas.get("miercoles")
            jueves = raw.get("jueves") or horas.get("jueves")
            viernes = raw.get("viernes") or horas.get("viernes")
            
            slots = parse_week_schedule(lunes, martes, miercoles, jueves, viernes)
            groups.append(
                GroupSlot(
                    grupo=str(raw.get("grupo", "")),
                    profesor=str(raw.get("profesor", "")),
                    asignatura=str(raw.get("asignatura", pending.nombre)),
                    slots=slots,
                    edificio=raw.get("edificio"),
                    aula=raw.get("aula"),
                    clave=clave,
                    lunes=lunes,
                    martes=martes,
                    miercoles=miercoles,
                    jueves=jueves,
                    viernes=viernes,
                )
            )
        subjects.append(
            SubjectWithGroups(
                name=pending.nombre,
                clave=clave,
                groups=groups,
            )
        )
    return subjects


def _build_option_item_response(group: GroupSlot) -> OptionItemResponse:
    """Construye la respuesta de un grupo a partir de un GroupSlot."""
    return OptionItemResponse(
        grupo=group.grupo,
        clave=group.clave or "",
        asignatura=group.asignatura,
        profesor=group.profesor,
        edificio=group.edificio,
        aula=group.aula,
        lunes=group.lunes,
        martes=group.martes,
        miercoles=group.miercoles,
        jueves=group.jueves,
        viernes=group.viernes,
    )


def _build_generate_response(
    scored_schedules: list[ScoredSchedule],
) -> GenerateResponse:
    """Construye la respuesta de generación con índices y puntuaciones."""
    results: list[ScheduleResultResponse] = []
    for idx, schedule in enumerate(scored_schedules):
        results.append(
            ScheduleResultResponse(
                index=idx,
                groups=[_build_option_item_response(g) for g in schedule.groups],
                scores=schedule.scores,
                total_score=schedule.total_score,
            )
        )
    return GenerateResponse(
        total_generated=len(scored_schedules),
        results=results,
    )


async def generate(
    db: AsyncSession,
    current_user: User,
    request: GenerateRequest,
) -> GenerateResponse:
    """Genera horarios válidos a partir de las materias pendientes del usuario.

    Requiere que el usuario tenga una cuenta SAES vinculada.
    """
    pending_subjects = await get_pending(db, current_user)
    selected = [p for p in pending_subjects if p.clave in request.subject_claves]

    if not selected:
        return GenerateResponse(total_generated=0, results=[])

    credential = await _get_credential_for_user(db, current_user.id)
    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay una cuenta SAES vinculada",
        )

    tokens = await get_saes_tokens_for_user(db, current_user.id)
    carrera = await _infer_user_career(db, current_user.id)
    claves = [p.clave for p in selected]
    raw_groups = await _fetch_subject_groups(credential.school, tokens, claves, carrera)

    subjects = _build_subjects_with_groups(selected, raw_groups)

    print(f"[schedule_service] Selected subjects count: {len(subjects)}")
    for subject in subjects:
        print(f"[schedule_service] Subject {subject.clave} ({subject.name}) got {len(subject.groups)} groups")

    for subject in subjects:
        if not subject.groups:
            print(f"[schedule_service] Subject {subject.clave} has 0 groups. Raising 422.")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                detail=f"La materia {subject.clave} no tiene grupos en el horario seleccionado",
            )

    filters: dict[str, Any] = {}
    if request.turno:
        filters["turno"] = request.turno

    hora_inicio = request.hora_inicio
    hora_fin = request.hora_fin

    if request.filters:
        from datetime import time
        if request.filters.start_min is not None:
            minutos = request.filters.start_min
            hora_inicio = time(hour=minutos // 60, minute=minutos % 60)
        if request.filters.start_max is not None:
            minutos = request.filters.start_max
            hora_fin = time(hour=minutos // 60, minute=minutos % 60)

    if hora_inicio:
        filters["hora_inicio"] = hora_inicio
    if hora_fin:
        filters["hora_fin"] = hora_fin

    if request.exclude_professors:
        filters["exclude_professors"] = request.exclude_professors

    if request.pinned_groups:
        filters["pinned_groups"] = request.pinned_groups

    scoring_map = {
        "compact": "compactness",
        "late": "late_start",
        "free": "free_days"
    }
    scoring_criteria = [scoring_map.get(c, c) for c in request.scoring]

    scored = generate_schedules(
        subjects=subjects,
        filters=filters,
        scoring_criteria=scoring_criteria,
        max_results=request.max_results,
    )

    return _build_generate_response(scored)


async def get_professors(
    db: AsyncSession,
    current_user: User,
) -> list[str]:
    """Retorna una lista de profesores distintos para las materias pendientes."""
    pending_subjects = await get_pending(db, current_user)
    if not pending_subjects:
        return []

    credential = await _get_credential_for_user(db, current_user.id)
    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay una cuenta SAES vinculada",
        )

    tokens = await get_saes_tokens_for_user(db, current_user.id)
    carrera = await _infer_user_career(db, current_user.id)
    claves = [p.clave for p in pending_subjects]
    raw_groups = await _fetch_subject_groups(credential.school, tokens, claves, carrera)

    professors = set()
    for raw in raw_groups:
        prof = raw.get("profesor")
        if prof:
            professors.add(str(prof).strip())
            
    return sorted(list(professors))


async def get_available_groups(
    db: AsyncSession,
    current_user: User,
) -> list[OptionItemResponse]:
    """Retorna todos los grupos disponibles en SAES para las materias pendientes."""
    pending_subjects = await get_pending(db, current_user)
    if not pending_subjects:
        return []

    credential = await _get_credential_for_user(db, current_user.id)
    if credential is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No hay una cuenta SAES vinculada",
        )

    tokens = await get_saes_tokens_for_user(db, current_user.id)
    carrera = await _infer_user_career(db, current_user.id)
    claves = [p.clave for p in pending_subjects]
    raw_groups = await _fetch_subject_groups(credential.school, tokens, claves, carrera)

    subjects_with_groups = _build_subjects_with_groups(pending_subjects, raw_groups)
    
    options = []
    for subject in subjects_with_groups:
        for group in subject.groups:
            options.append(_build_option_item_response(group))
            
    return options


async def save_schedule(
    db: AsyncSession,
    current_user: User,
    request: SaveScheduleRequest,
) -> SavedScheduleResponse:
    """Guarda un horario generado para el usuario actual."""
    saved = SavedSchedule(
        user_id=current_user.id,
        name=request.name,
        is_favorite=False,
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    db.add(saved)
    await db.flush()
    await db.refresh(saved)

    for order_index, group in enumerate(request.groups):
        item = OptionItem(
            schedule_id=saved.id,
            grupo=group.grupo,
            clave=group.clave,
            asignatura=group.asignatura,
            profesor=group.profesor,
            edificio=group.edificio,
            aula=group.aula,
            lunes=group.lunes,
            martes=group.martes,
            miercoles=group.miercoles,
            jueves=group.jueves,
            viernes=group.viernes,
            order_index=order_index,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        db.add(item)

    await db.commit()
    await db.refresh(saved)
    return SavedScheduleResponse.model_validate(saved)


async def get_saved_schedules(
    db: AsyncSession,
    current_user: User,
) -> list[SavedScheduleResponse]:
    """Retorna todos los horarios guardados del usuario."""
    result = await db.execute(
        select(SavedSchedule)
        .where(SavedSchedule.user_id == current_user.id)
        .order_by(SavedSchedule.created_at.desc())
    )
    schedules = result.scalars().all()
    return [SavedScheduleResponse.model_validate(s) for s in schedules]


async def toggle_favorite(
    db: AsyncSession,
    current_user: User,
    schedule_id: uuid.UUID,
) -> SavedScheduleResponse:
    """Alterna el estado de favorito de un horario guardado."""
    result = await db.execute(
        select(SavedSchedule).where(
            SavedSchedule.id == schedule_id,
            SavedSchedule.user_id == current_user.id,
        )
    )
    saved: SavedSchedule | None = result.scalar_one_or_none()
    if saved is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Horario no encontrado",
        )

    saved.is_favorite = not saved.is_favorite
    saved.updated_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(saved)
    return SavedScheduleResponse.model_validate(saved)


async def delete_saved_schedule(
    db: AsyncSession,
    current_user: User,
    schedule_id: uuid.UUID,
) -> None:
    """Elimina un horario guardado del usuario actual."""
    result = await db.execute(
        select(SavedSchedule).where(
            SavedSchedule.id == schedule_id,
            SavedSchedule.user_id == current_user.id,
        )
    )
    saved: SavedSchedule | None = result.scalar_one_or_none()
    if saved is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Horario no encontrado",
        )

    await db.delete(saved)
    await db.commit()
