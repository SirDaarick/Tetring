"""Algoritmo de backtracking para generación de horarios escolares.

Incluye la representación de franjas horarias, el parseo de cadenas de
horario, la generación de combinaciones válidas sin empalmes con
verificación hacia adelante (forward checking) y funciones de puntuación.

La representación de franja usa el formato ``day_index * 100 + slot_index``:

- ``day_index``: 0 = Lunes, 1 = Martes, ..., 4 = Viernes.
- ``slot_index``: ``hora * 2 + (1 si minuto >= 30 else 0)``; rango 0–43
  para horarios de 06:00 a 22:00.
"""

from dataclasses import dataclass, field
from datetime import time
from typing import Any

MAX_SCHEDULES: int = 20000

_DIAS_SEMANA: list[str] = ["lunes", "martes", "miercoles", "jueves", "viernes"]


@dataclass
class GroupSlot:
    """Opción de grupo para una asignatura con su horario semanal."""

    grupo: str
    profesor: str
    asignatura: str
    slots: set[int] = field(default_factory=set)
    edificio: str | None = None
    aula: str | None = None
    clave: str | None = None
    lunes: str | None = None
    martes: str | None = None
    miercoles: str | None = None
    jueves: str | None = None
    viernes: str | None = None

    def __hash__(self) -> int:
        return hash(
            (self.grupo, self.profesor, self.asignatura, frozenset(self.slots))
        )

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, GroupSlot):
            return NotImplemented
        return (
            self.grupo == other.grupo
            and self.profesor == other.profesor
            and self.asignatura == other.asignatura
            and self.slots == other.slots
        )


@dataclass
class SubjectWithGroups:
    """Asignatura con todas las opciones de grupo disponibles."""

    name: str
    clave: str
    groups: list[GroupSlot] = field(default_factory=list)


@dataclass
class ScoredSchedule:
    """Horario generado con puntuaciones por criterio."""

    groups: list[GroupSlot] = field(default_factory=list)
    scores: dict[str, float] = field(default_factory=dict)
    total_score: float = 0.0


def parse_time_slot(time_str: str) -> set[int]:
    """Convierte una cadena ``HH:MM-HH:MM`` en un conjunto de índices de franja.

    Parámetros
    ----------
    time_str:
        Cadena con el formato ``HH:MM-HH:MM``. También acepta cadenas vacías,
        ``"X"`` o valores malformados, devolviendo un conjunto vacío en esos
        casos.

    Ejemplos
    --------
    >>> parse_time_slot("07:00-08:30")
    {14, 15, 16}
    """
    result: set[int] = set()
    if not time_str:
        return result
    cleaned = time_str.strip()
    if cleaned.upper() == "X" or cleaned == "":
        return result
    if "-" not in cleaned:
        return result

    try:
        start_part, end_part = cleaned.split("-", 1)
        start_h, start_m = start_part.split(":")
        end_h, end_m = end_part.split(":")
        start_h = int(start_h)
        start_m = int(start_m)
        end_h = int(end_h)
        end_m = int(end_m)
    except (ValueError, AttributeError):
        return result

    if not (0 <= start_h < 24 and 0 <= start_m < 60):
        return result
    if not (0 <= end_h < 24 and 0 <= end_m < 60):
        return result

    start_idx = start_h * 2 + (1 if start_m >= 30 else 0)
    end_idx = end_h * 2 + (1 if end_m >= 30 else 0)
    if end_idx <= start_idx:
        return result

    return set(range(start_idx, end_idx))


def parse_day_schedule(day_str: str, day_index: int) -> set[int]:
    """Parsea el horario de un día a franjas globales ``día * 100 + franja``.

    Parámetros
    ----------
    day_str:
        Cadena de horario del día en formato ``HH:MM-HH:MM``.
    day_index:
        Índice del día de la semana (0 = Lunes, ..., 4 = Viernes).

    Retorna
    -------
    Conjunto de franjas globales para ese día.
    """
    return {day_index * 100 + slot for slot in parse_time_slot(day_str)}


def parse_week_schedule(
    lunes: str | None = None,
    martes: str | None = None,
    miercoles: str | None = None,
    jueves: str | None = None,
    viernes: str | None = None,
) -> set[int]:
    """Parsea los cinco días de la semana en un conjunto de franjas globales.

    Los valores ``None`` o vacíos se ignoran.
    """
    day_values = [lunes, martes, miercoles, jueves, viernes]
    slots: set[int] = set()
    for idx, value in enumerate(day_values):
        slots |= parse_day_schedule(value or "", idx)
    return slots


def time_to_slot(value: time) -> int:
    """Convierte un objeto ``time`` a índice de franja horaria."""
    return value.hour * 2 + (1 if value.minute >= 30 else 0)


def _detect_turno(grupo: str) -> str:
    """Detecta el turno a partir de la tercera letra (índice 2) del grupo.

    Ejemplos:
    - 8BM1: M -> Matutino
    - 8BV1: V -> Vespertino
    """
    if not grupo or len(grupo) < 3:
        return "Matutino"
    turno_char = grupo[2].upper()
    if turno_char == "V":
        return "Vespertino"
    elif turno_char == "M":
        return "Matutino"
    return "Mixto"


def _group_time_range(slots: set[int]) -> tuple[int, int] | None:
    """Retorna ``(slot_inicio, slot_fin)`` para un conjunto de franjas."""
    if not slots:
        return None
    slot_indices = {slot % 100 for slot in slots}
    return min(slot_indices), max(slot_indices) + 1


def _apply_filters(
    subjects: list[SubjectWithGroups],
    filters: dict[str, Any],
) -> list[SubjectWithGroups]:
    """Aplica turno, rango horario y profesores a las opciones de cada materia."""
    turno: str | None = filters.get("turno")
    if turno:
        turno = turno.strip().lower()
        
    hora_inicio: time | None = filters.get("hora_inicio")
    hora_fin: time | None = filters.get("hora_fin")
    profesores: list[str] | None = filters.get("profesores")
    exclude_professors: list[str] | None = filters.get("exclude_professors")

    start_slot = time_to_slot(hora_inicio) if isinstance(hora_inicio, time) else None
    end_slot = time_to_slot(hora_fin) if isinstance(hora_fin, time) else None

    profesores_norm: set[str] = set()
    if profesores:
        profesores_norm = {str(p).strip().lower() for p in profesores}

    exclude_prof_norm: set[str] = set()
    if exclude_professors:
        exclude_prof_norm = {str(p).strip().lower() for p in exclude_professors}

    pinned_groups: dict[str, str] | None = filters.get("pinned_groups")

    filtered_subjects: list[SubjectWithGroups] = []
    for subject in subjects:
        valid_groups: list[GroupSlot] = []
        pinned_grupo = pinned_groups.get(subject.clave) if pinned_groups else None
        
        for group in subject.groups:
            if pinned_grupo and group.grupo != pinned_grupo:
                continue

            if turno and turno != "mixto":
                group_turno = _detect_turno(group.grupo).lower()
                if group_turno != turno:
                    continue

            group_prof = group.profesor.strip().lower()

            if profesores_norm:
                if group_prof not in profesores_norm:
                    continue

            if exclude_prof_norm:
                if group_prof in exclude_prof_norm:
                    continue

            time_range = _group_time_range(group.slots)
            if time_range is None:
                continue
            group_start, group_end = time_range

            if start_slot is not None and group_start < start_slot:
                continue
            if end_slot is not None and group_end > end_slot:
                continue

            valid_groups.append(group)

        filtered_subjects.append(
            SubjectWithGroups(
                name=subject.name,
                clave=subject.clave,
                groups=valid_groups,
            )
        )

    return filtered_subjects


def _forward_check(
    remaining_subjects: list[SubjectWithGroups],
    occupied: set[int],
) -> bool:
    """Verifica que cada materia restante tenga al menos un grupo compatible.

    Retorna ``False`` inmediatamente si alguna materia no tiene opciones
    válidas con las franjas ya ocupadas.
    """
    for subject in remaining_subjects:
        has_option = any(not (group.slots & occupied) for group in subject.groups)
        if not has_option:
            return False
    return True


def _backtrack(
    subjects: list[SubjectWithGroups],
    idx: int,
    current: list[GroupSlot],
    occupied: set[int],
    results: list[list[GroupSlot]],
) -> None:
    """Backtracking recursivo con verificación hacia adelante."""
    if len(results) >= MAX_SCHEDULES:
        return
    if idx == len(subjects):
        results.append(current.copy())
        return

    for group in subjects[idx].groups:
        if group.slots & occupied:
            continue

        current.append(group)
        remaining = subjects[idx + 1 :]
        new_occupied = occupied | group.slots

        if _forward_check(remaining, new_occupied):
            _backtrack(subjects, idx + 1, current, new_occupied, results)

        current.pop()


def generate_schedules(
    subjects: list[SubjectWithGroups],
    filters: dict[str, Any] | None = None,
    scoring_criteria: list[str] | None = None,
    max_results: int = 50,
) -> list[ScoredSchedule]:
    """Genera horarios válidos sin empalmes y los ordena por puntuación.

    Parámetros
    ----------
    subjects:
        Lista de asignaciones, cada una con sus opciones de grupo.
    filters:
        Diccionario con ``turno`` ("Matutino", "Vespertino" o "Mixto"),
        ``hora_inicio`` y ``hora_fin`` como objetos ``time``, y opcionalmente
        ``profesores`` como lista de nombres.
    scoring_criteria:
        Lista de criterios a evaluar: ``"compactness"``, ``"late_start"``,
        ``"free_days"``.
    max_results:
        Cantidad máxima de horarios a retornar (por defecto 50).

    Retorna
    -------
    Lista de horarios puntuados ordenados de menor a mayor puntuación total.
    """
    if filters is None:
        filters = {}
    if scoring_criteria is None:
        scoring_criteria = ["compactness"]

    filtered_subjects = _apply_filters(subjects, filters)
    # Heurística MRV: ordenar materias por menor cantidad de opciones primero.
    sorted_subjects = sorted(filtered_subjects, key=lambda s: len(s.groups))

    results: list[list[GroupSlot]] = []
    _backtrack(sorted_subjects, 0, [], set(), results)

    scored = _score_schedules(results, scoring_criteria)
    scored.sort(key=lambda s: s.total_score)
    return scored[:max_results]


def _score_schedules(
    schedules: list[list[GroupSlot]],
    criteria: list[str],
) -> list[ScoredSchedule]:
    """Puntúa todos los horarios generados según los criterios solicitados."""
    if not schedules:
        return []

    raw_scores: list[dict[str, float]] = []
    for groups in schedules:
        raw_scores.append(
            {
                "compactness": score_compactness(groups),
                "late_start": score_late_start(groups),
                "free_days": score_free_days(groups),
            }
        )

    scored: list[ScoredSchedule] = []
    for groups, scores in zip(schedules, raw_scores):
        filtered_scores = {c: scores[c] for c in criteria if c in scores}
        total = _normalize_and_sum(scores, criteria, raw_scores)
        scored.append(
            ScoredSchedule(
                groups=groups,
                scores=filtered_scores,
                total_score=total,
            )
        )
    return scored


def _normalize_and_sum(
    scores: dict[str, float],
    criteria: list[str],
    all_scores: list[dict[str, float]],
) -> float:
    """Normaliza cada criterio al rango [0, 1] y suma los valores.

    Para todos los criterios se asume que un valor más bajo representa una
    mejor puntuación.
    """
    total = 0.0
    for criterion in criteria:
        values = [s[criterion] for s in all_scores]
        min_val = min(values)
        max_val = max(values)
        val = scores[criterion]
        if max_val > min_val:
            normalized = (val - min_val) / (max_val - min_val)
        else:
            normalized = 0.0
        total += normalized
    return total


def score_compactness(schedule: list[GroupSlot]) -> float:
    """Menos horas libres = mejor (puntuación más baja).

    Calcula, para cada día con clases, la cantidad de medias horas libres
    entre la primera y la última clase.
    """
    day_slots: dict[int, list[int]] = {i: [] for i in range(5)}
    for group in schedule:
        for slot in group.slots:
            day_idx = slot // 100
            slot_idx = slot % 100
            if 0 <= day_idx < 5:
                day_slots[day_idx].append(slot_idx)

    free_hours = 0.0
    for slots in day_slots.values():
        if not slots:
            continue
        free_hours += (max(slots) - min(slots) + 1 - len(slots)) * 0.5

    return free_hours


def score_late_start(schedule: list[GroupSlot]) -> float:
    """Preferir horarios que empiecen más tarde. Menor puntuación = mejor."""
    if not schedule:
        return 0.0
    first_slot = min(
        slot % 100 for group in schedule for slot in group.slots
    )
    return -float(first_slot)


def score_free_days(schedule: list[GroupSlot]) -> float:
    """Preferir más días libres. Menor puntuación = mejor."""
    active_days = {
        slot // 100
        for group in schedule
        for slot in group.slots
        if 0 <= slot // 100 < 5
    }
    return -float(5 - len(active_days))
