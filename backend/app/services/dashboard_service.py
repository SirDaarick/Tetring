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


def _parse_semester_period(periodo: str | None) -> int:
    """Convierte un periodo curricular (números arábigos o romanos) a entero."""
    if not periodo:
        return 0
    p = periodo.strip().upper()
    try:
        return int(p)
    except ValueError:
        pass
    
    # Mapeo de números romanos del SAES (I al X)
    roman_map = {
        "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5,
        "VI": 6, "VII": 7, "VIII": 8, "IX": 9, "X": 10,
        "1": 1, "2": 2, "3": 3, "4": 4, "5": 5,
        "6": 6, "7": 7, "8": 8, "9": 9, "10": 10
    }
    return roman_map.get(p, 0)


def _parse_escom_materia(clave: str) -> tuple[str | None, str | None]:
    """Extrae el (semestre, tipo) de una clave de materia en ESCOM.

    Soporta formato antiguo (ej. I642) y nuevo (ej. 3S6415, 4S6415, 5S6415).
    """
    if not clave or len(clave) < 3:
        return None, None

    index_carrera = -1
    if clave[0].isalpha():
        index_carrera = 0
    elif len(clave) >= 4 and clave[1].isalpha():
        index_carrera = 1

    if index_carrera != -1 and len(clave) > index_carrera + 2:
        semestre = clave[index_carrera + 1]
        tipo = clave[index_carrera + 2]
        return semestre, tipo

    return None, None


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
        select(KardexEntry).where(KardexEntry.user_id == current_user.id)
    )
    kardex_entries = list(kardex_result.scalars().all())
    kardex_claves = {entry.clave.strip().upper() for entry in kardex_entries if entry.clave}

    result = await db.execute(
        select(CurriculumCourse)
        .where(CurriculumCourse.user_id == current_user.id)
        .order_by(CurriculumCourse.periodo)
    )
    curriculum_courses = list(result.scalars().all())

    # Detectar escuela
    from app.models.saes_credential import SaesCredential
    saes_result = await db.execute(
        select(SaesCredential).where(SaesCredential.user_id == current_user.id)
    )
    saes_credential = saes_result.scalar_one_or_none()
    school = (saes_credential.school if saes_credential else "").lower()
    es_escom = school == "escom"
    es_esiatec = school == "esiatec"

    # Mapeo de materias de currícula por clave
    curriculum_by_clave = {
        c.clave.strip().upper(): c for c in curriculum_courses if c.clave
    }

    # Contar optativas aprobadas por semestre
    optativas_aprobadas_por_semestre: defaultdict[int, int] = defaultdict(int)
    for entry in kardex_entries:
        clave = entry.clave.strip().upper()
        calif = _parse_grade(entry.calificacion)
        aprobada = (calif is not None and calif >= 6.0) or entry.calificacion.upper() in ["AC", "APROBADO", "EXS"]
        if aprobada:
            if es_escom:
                semestre, tipo = _parse_escom_materia(clave)
                if tipo in ['4', '5']:
                    try:
                        sem_int = int(semestre) if semestre else 0
                        optativas_aprobadas_por_semestre[sem_int] += 1
                    except ValueError:
                        pass
            elif es_esiatec:
                course = curriculum_by_clave.get(clave)
                tipo_c = (course.tipo or "").upper() if course else ""
                if "OPTATIVA" in tipo_c or "ELECTIVA" in tipo_c or (course and "OPTATIVA" in (course.nombre or "").upper()):
                    sem_int = _parse_semester_period(course.periodo) if course else 0
                    if sem_int > 0:
                        optativas_aprobadas_por_semestre[sem_int] += 1

    # Inferir la carrera del alumno
    from collections import Counter
    carreras_detectadas = []
    for course in curriculum_courses:
        if course.clave.strip().upper() in kardex_claves and course.carrera:
            carreras_detectadas.append(course.carrera)

    carrera_inferida = None
    if carreras_detectadas:
        carrera_inferida = Counter(carreras_detectadas).most_common(1)[0][0]

    vistas = set()
    pending: list[PendingSubjectResponse] = []
    for course in curriculum_courses:
        clave_norm = course.clave.strip().upper()
        if clave_norm in vistas:
            continue
        vistas.add(clave_norm)

        # Filtro de carrera: Si inferimos la carrera, solo incluimos materias de esta
        if carrera_inferida and course.carrera != carrera_inferida:
            continue

        semestre_val = _parse_semester_period(course.periodo)
        tipo_upper = (course.tipo or "").upper()
        nombre_upper = (course.nombre or "").upper()
        is_optativa = "OPTATIVA" in tipo_upper or "ELECTIVA" in tipo_upper or "OPTATIVA" in nombre_upper

        # Filtro de cupo de optativas para ESCOM
        if es_escom:
            semestre, tipo = _parse_escom_materia(clave_norm)
            if tipo in ['4', '5']:
                if semestre == '6' and optativas_aprobadas_por_semestre[6] >= 2:
                    continue
                if semestre == '7' and optativas_aprobadas_por_semestre[7] >= 2:
                    continue

        # Filtro de cupo de optativas para ESIATEC Plan 2023:
        # 6.° -> 1 optativa, 7.° -> 2 optativas, 8.° -> 2 optativas, 9.° -> 1 optativa, 10.° -> 1 electiva
        if es_esiatec and is_optativa:
            if semestre_val == 6 and optativas_aprobadas_por_semestre[6] >= 1:
                continue
            if semestre_val == 7 and optativas_aprobadas_por_semestre[7] >= 2:
                continue
            if semestre_val == 8 and optativas_aprobadas_por_semestre[8] >= 2:
                continue
            if semestre_val == 9 and optativas_aprobadas_por_semestre[9] >= 1:
                continue
            if semestre_val == 10 and optativas_aprobadas_por_semestre[10] >= 1:
                continue

        if clave_norm not in kardex_claves:
            # Servicio Social es un trámite/crédito administrativo, no una materia con horario de clases presencial
            if "SERVICIO SOCIAL" in nombre_upper:
                continue

            pending.append(
                PendingSubjectResponse(
                    clave=course.clave,
                    nombre=course.nombre,
                    creditos=course.creditos,
                    periodo_curricular=course.periodo,
                    semestre=semestre_val,
                    tipo=course.tipo,
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

    kardex_claves = {entry.clave.strip().upper() for entry in kardex_entries if entry.clave}
    passed_claves = {
        entry.clave.strip().upper()
        for entry in kardex_entries
        if entry.clave and (grade := _parse_grade(entry.calificacion)) is not None
        and grade >= 6.0
    }

    curriculum_result = await db.execute(
        select(CurriculumCourse).where(
            CurriculumCourse.user_id == current_user.id
        )
    )
    curriculum_courses = list(curriculum_result.scalars().all())
    curriculum_by_clave = {course.clave.strip().upper(): course for course in curriculum_courses if course.clave}

    # Inferir la carrera del alumno
    from collections import Counter
    carreras_detectadas = []
    for course in curriculum_courses:
        if course.clave and course.clave.strip().upper() in kardex_claves and course.carrera:
            carreras_detectadas.append(course.carrera)

    carrera_inferida = None
    if carreras_detectadas:
        carrera_inferida = Counter(carreras_detectadas).most_common(1)[0][0]

    creditos_completados = 0
    for clave in passed_claves:
        course = curriculum_by_clave.get(clave)
        if course and course.creditos:
            try:
                creditos_completados += int(course.creditos)
            except ValueError:
                continue

    from app.models.saes_credential import SaesCredential

    saes_result = await db.execute(
        select(SaesCredential).where(SaesCredential.user_id == current_user.id)
    )
    saes_credential = saes_result.scalar_one_or_none()
    last_sync_at = saes_credential.updated_at.isoformat() if saes_credential else None
    school = (saes_credential.school if saes_credential else "").lower()
    es_escom = school == "escom"
    es_esiatec = school == "esiatec"

    # Contar optativas aprobadas por semestre
    optativas_aprobadas_por_semestre: defaultdict[int, int] = defaultdict(int)
    for entry in kardex_entries:
        clave = entry.clave.strip().upper()
        calif = _parse_grade(entry.calificacion)
        aprobada = (calif is not None and calif >= 6.0) or entry.calificacion.upper() in ["AC", "APROBADO", "EXS"]
        if aprobada:
            if es_escom:
                semestre, tipo = _parse_escom_materia(clave)
                if tipo in ['4', '5']:
                    try:
                        sem_int = int(semestre) if semestre else 0
                        optativas_aprobadas_por_semestre[sem_int] += 1
                    except ValueError:
                        pass
            elif es_esiatec:
                course = curriculum_by_clave.get(clave)
                tipo_c = (course.tipo or "").upper() if course else ""
                if "OPTATIVA" in tipo_c or "ELECTIVA" in tipo_c or (course and "OPTATIVA" in (course.nombre or "").upper()):
                    sem_int = _parse_semester_period(course.periodo) if course else 0
                    if sem_int > 0:
                        optativas_aprobadas_por_semestre[sem_int] += 1

    vistas = set()
    pending_courses = []
    for course in curriculum_courses:
        clave_norm = course.clave.strip().upper()
        if clave_norm in vistas:
            continue
        vistas.add(clave_norm)

        # Filtro de carrera
        if carrera_inferida and course.carrera != carrera_inferida:
            continue

        semestre_val = _parse_semester_period(course.periodo)
        tipo_upper = (course.tipo or "").upper()
        nombre_upper = (course.nombre or "").upper()
        is_optativa = "OPTATIVA" in tipo_upper or "ELECTIVA" in tipo_upper or "OPTATIVA" in nombre_upper

        # Filtro de optativas para ESCOM
        if es_escom:
            semestre, tipo = _parse_escom_materia(clave_norm)
            if tipo in ['4', '5']:
                if semestre == '6' and optativas_aprobadas_por_semestre[6] >= 2:
                    continue
                if semestre == '7' and optativas_aprobadas_por_semestre[7] >= 2:
                    continue

        # Filtro de cupo de optativas para ESIATEC Plan 2023:
        # 6.° -> 1 optativa, 7.° -> 2 optativas, 8.° -> 2 optativas, 9.° -> 1 optativa, 10.° -> 1 electiva
        if es_esiatec and is_optativa:
            if semestre_val == 6 and optativas_aprobadas_por_semestre[6] >= 1:
                continue
            if semestre_val == 7 and optativas_aprobadas_por_semestre[7] >= 2:
                continue
            if semestre_val == 8 and optativas_aprobadas_por_semestre[8] >= 2:
                continue
            if semestre_val == 9 and optativas_aprobadas_por_semestre[9] >= 1:
                continue
            if semestre_val == 10 and optativas_aprobadas_por_semestre[10] >= 1:
                continue

        if clave_norm not in kardex_claves:
            if "SERVICIO SOCIAL" in nombre_upper:
                continue
            pending_courses.append(course)

    # Calcular obligatorias pendientes y optativas restantes requeridas
    obligatorias_pendientes = 0
    for course in pending_courses:
        tipo_u = (course.tipo or "").upper()
        nombre_u = (course.nombre or "").upper()
        if not ("OPTATIVA" in tipo_u or "ELECTIVA" in tipo_u or "OPTATIVA" in nombre_u):
            obligatorias_pendientes += 1

    optativas_restantes = 0
    if es_esiatec:
        # Requeridas: 6.° -> 1, 7.° -> 2, 8.° -> 2, 9.° -> 1, 10.° -> 1
        optativas_restantes += max(0, 1 - optativas_aprobadas_por_semestre[6])
        optativas_restantes += max(0, 2 - optativas_aprobadas_por_semestre[7])
        optativas_restantes += max(0, 2 - optativas_aprobadas_por_semestre[8])
        optativas_restantes += max(0, 1 - optativas_aprobadas_por_semestre[9])
        optativas_restantes += max(0, 1 - optativas_aprobadas_por_semestre[10])
    elif es_escom:
        # Requeridas: 6.° -> 2, 7.° -> 2
        optativas_restantes += max(0, 2 - optativas_aprobadas_por_semestre[6])
        optativas_restantes += max(0, 2 - optativas_aprobadas_por_semestre[7])
    else:
        # Genérico: contar las optativas únicas presentes en pending
        optativas_restantes = len(pending_courses) - obligatorias_pendientes

    materias_pendientes_total = obligatorias_pendientes + optativas_restantes

    by_semester: defaultdict[str, int] = defaultdict(int)
    for course in pending_courses:
        by_semester[course.periodo or "Sin periodo"] += 1

    pending_by_semester = [
        PendingBySemester(periodo=periodo, materias=cantidad)
        for periodo, cantidad in sorted(
            by_semester.items(),
            key=lambda item: _parse_semester_period(item[0]) if _parse_semester_period(item[0]) > 0 else 99
        )
    ]

    schedule_result = await db.execute(
        select(CurrentSchedule).where(
            CurrentSchedule.user_id == current_user.id
        )
    )
    tiene_horario_actual = schedule_result.scalars().first() is not None

    return DashboardSummaryResponse(
        total_cursadas=total_cursadas,
        promedio_general=promedio_general,
        creditos_completados=creditos_completados if creditos_completados else None,
        materias_pendientes=materias_pendientes_total,
        pending_by_semester=pending_by_semester,
        tiene_horario_actual=tiene_horario_actual,
        cursadas=total_cursadas,
        promedio=promedio_general,
        pendientes=materias_pendientes_total,
        obligatorias_pendientes=obligatorias_pendientes,
        optativas_pendientes=optativas_restantes,
        last_sync_at=last_sync_at,
    )
