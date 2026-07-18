"""Servicios de consulta para el dashboard académico.

Calcula resúmenes, kárdex, materias pendientes y horario actual a partir de
los datos sincronizados en la base de datos.
"""

from collections import defaultdict

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.curriculum_course import CurriculumCourse
from app.models.current_schedule import CurrentSchedule
from app.models.kardex_entry import KardexEntry
from app.models.user import User
from app.schemas.dashboard import (
    DashboardSummaryResponse,
    KardexEntryResponse,
    PendingBySemester,
    PendingSubjectResponse,
)


def _parse_grade(calificacion: str | None) -> float | None:
    """Convierte una calificación a ``float``; devuelve ``None`` si no es numérica."""
    if calificacion is None:
        return None
    try:
        return float(calificacion)
    except ValueError:
        return None


async def get_kardex(
    db: AsyncSession,
    current_user: User,
) -> list[KardexEntryResponse]:
    """Retorna todas las entradas del kárdex del usuario ordenadas por periodo."""
    result = await db.execute(
        select(KardexEntry)
        .where(KardexEntry.user_id == current_user.id)
        .order_by(KardexEntry.periodo)
    )
    entries = result.scalars().all()
    return [KardexEntryResponse.model_validate(entry) for entry in entries]


async def get_pending(
    db: AsyncSession,
    current_user: User,
) -> list[PendingSubjectResponse]:
    """Retorna las materias de la currícula que aún no aparecen en el kárdex.

    El cálculo se realiza por clave de asignatura y se ordena por periodo
    curricular.
    """
    kardex_result = await db.execute(
        select(KardexEntry.clave).where(KardexEntry.user_id == current_user.id)
    )
    kardex_claves = {row[0] for row in kardex_result.all()}

    result = await db.execute(
        select(CurriculumCourse)
        .where(CurriculumCourse.user_id == current_user.id)
        .order_by(CurriculumCourse.periodo)
    )

    pending: list[PendingSubjectResponse] = []
    for course in result.scalars().all():
        if course.clave not in kardex_claves:
            pending.append(
                PendingSubjectResponse(
                    clave=course.clave,
                    nombre=course.nombre,
                    creditos=course.creditos,
                    periodo_curricular=course.periodo,
                )
            )

    return pending


async def get_current_schedule(
    db: AsyncSession,
    current_user: User,
) -> list[CurrentSchedule]:
    """Retorna los grupos del horario actual del usuario."""
    result = await db.execute(
        select(CurrentSchedule)
        .where(CurrentSchedule.user_id == current_user.id)
        .order_by(CurrentSchedule.asignatura)
    )
    return list(result.scalars().all())


async def get_summary(
    db: AsyncSession,
    current_user: User,
) -> DashboardSummaryResponse:
    """Calcula el resumen académico del usuario.

    Incluye total de materias cursadas, promedio general, créditos completados,
    materias pendientes agrupadas por periodo y la existencia de un horario
    actual.
    """
    kardex_result = await db.execute(
        select(KardexEntry).where(KardexEntry.user_id == current_user.id)
    )
    kardex_entries = list(kardex_result.scalars().all())
    total_cursadas = len(kardex_entries)

    numeric_grades = [
        grade
        for entry in kardex_entries
        if (grade := _parse_grade(entry.calificacion)) is not None
    ]
    promedio_general = (
        sum(numeric_grades) / len(numeric_grades) if numeric_grades else None
    )

    kardex_claves = {entry.clave for entry in kardex_entries}
    passed_claves = {
        entry.clave
        for entry in kardex_entries
        if (grade := _parse_grade(entry.calificacion)) is not None
        and grade >= 6.0
    }

    curriculum_result = await db.execute(
        select(CurriculumCourse).where(
            CurriculumCourse.user_id == current_user.id
        )
    )
    curriculum_courses = list(curriculum_result.scalars().all())
    curriculum_by_clave = {course.clave: course for course in curriculum_courses}

    creditos_completados = 0
    for clave in passed_claves:
        course = curriculum_by_clave.get(clave)
        if course and course.creditos:
            try:
                creditos_completados += int(course.creditos)
            except ValueError:
                continue

    pending_courses = [
        course for course in curriculum_courses if course.clave not in kardex_claves
    ]
    materias_pendientes = len(pending_courses)

    by_semester: defaultdict[str, int] = defaultdict(int)
    for course in pending_courses:
        by_semester[course.periodo or "Sin periodo"] += 1

    pending_by_semester = [
        PendingBySemester(periodo=periodo, materias=cantidad)
        for periodo, cantidad in sorted(by_semester.items())
    ]

    schedule_result = await db.execute(
        select(CurrentSchedule).where(
            CurrentSchedule.user_id == current_user.id
        )
    )
    tiene_horario_actual = schedule_result.scalar_one_or_none() is not None

    return DashboardSummaryResponse(
        total_cursadas=total_cursadas,
        promedio_general=promedio_general,
        creditos_completados=creditos_completados if creditos_completados else None,
        materias_pendientes=materias_pendientes,
        pending_by_semester=pending_by_semester,
        tiene_horario_actual=tiene_horario_actual,
    )
