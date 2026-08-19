"""Pruebas para el algoritmo de generación de horarios y persistencia.

Incluye validación de parseo de franjas horarias, backtracking con
verificación hacia adelante, funciones de puntuación y guardado de
horarios favoritos.
"""

import uuid

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.algorithms import scheduler as scheduler_module
from app.algorithms.scheduler import (
    GroupSlot,
    ScoredSchedule,
    SubjectWithGroups,
    generate_schedules,
    parse_day_schedule,
    parse_time_slot,
    parse_week_schedule,
    score_compactness,
    score_free_days,
    score_late_start,
)
from app.models.user import User
from app.schemas.schedule import OptionItemResponse, SaveScheduleRequest
from app.services import schedule_service


def test_parse_time_slot_valid() -> None:
    """Un horario válido se convierte al conjunto de franjas esperado."""
    slots = parse_time_slot("07:00-08:30")
    # 07:00 -> 14, 07:30 -> 15, 08:00 -> 16 (08:30 -> 17 es exclusivo)
    assert slots == {14, 15, 16}


def test_parse_time_slot_empty() -> None:
    """Una cadena vacía produce un conjunto de franjas vacío."""
    assert parse_time_slot("") == set()
    assert parse_time_slot("   ") == set()
    assert parse_time_slot("X") == set()
    assert parse_time_slot("x") == set()


def test_parse_time_slot_malformed() -> None:
    """Cadenas malformadas no lanzan excepciones y devuelven conjunto vacío."""
    assert parse_time_slot("07:00") == set()
    assert parse_time_slot("no-es-horario") == set()
    assert parse_time_slot("25:00-26:00") == set()
    assert parse_time_slot("07:00-07:00") == set()


def test_parse_day_schedule_uses_day_index() -> None:
    """El índice del día se incorpora a la representación global."""
    slots = parse_day_schedule("07:00-08:30", 2)
    assert slots == {214, 215, 216}


def test_parse_week_schedule_combines_days() -> None:
    """El horario semanal combina correctamente los cinco días."""
    slots = parse_week_schedule(
        lunes="07:00-08:30",
        martes="",
        miercoles="09:00-10:00",
        jueves=None,
        viernes="X",
    )
    assert slots == {14, 15, 16, 218, 219}


def _build_group(
    grupo: str,
    asignatura: str,
    clave: str,
    dias: list[str],
) -> GroupSlot:
    """Helper para construir un GroupSlot a partir de cadenas de día."""
    slots = parse_week_schedule(
        lunes=dias[0] if len(dias) > 0 else None,
        martes=dias[1] if len(dias) > 1 else None,
        miercoles=dias[2] if len(dias) > 2 else None,
        jueves=dias[3] if len(dias) > 3 else None,
        viernes=dias[4] if len(dias) > 4 else None,
    )
    return GroupSlot(
        grupo=grupo,
        profesor="Profesor Test",
        asignatura=asignatura,
        clave=clave,
        slots=slots,
        lunes=dias[0] if len(dias) > 0 else None,
        martes=dias[1] if len(dias) > 1 else None,
        miercoles=dias[2] if len(dias) > 2 else None,
        jueves=dias[3] if len(dias) > 3 else None,
        viernes=dias[4] if len(dias) > 4 else None,
    )


def test_generate_returns_valid_schedules() -> None:
    """La generación retorna horarios válidos sin empalmes."""
    subjects = [
        SubjectWithGroups(
            name="Matemáticas",
            clave="MAT-101",
            groups=[
                _build_group("1AM1", "Matemáticas", "MAT-101", ["07:00-08:30", "", "", "", ""]),
                _build_group("1AM2", "Matemáticas", "MAT-101", ["09:00-10:30", "", "", "", ""]),
            ],
        ),
        SubjectWithGroups(
            name="Física",
            clave="FIS-101",
            groups=[
                _build_group("1AF1", "Física", "FIS-101", ["", "07:00-08:30", "", "", ""]),
                _build_group("1AF2", "Física", "FIS-101", ["", "09:00-10:30", "", "", ""]),
            ],
        ),
    ]

    result = generate_schedules(subjects, max_results=10)
    assert len(result) == 4
    for scored in result:
        assert len(scored.groups) == 2
        occupied: set[int] = set()
        for group in scored.groups:
            assert not (group.slots & occupied)
            occupied |= group.slots


def test_no_overlap_in_results() -> None:
    """Todos los horarios generados deben tener cero empalmes."""
    subjects = [
        SubjectWithGroups(
            name="Materia A",
            clave="A-101",
            groups=[
                _build_group("G1", "Materia A", "A-101", ["07:00-08:30", "", "", "", ""]),
                _build_group("G2", "Materia A", "A-101", ["08:30-10:00", "", "", "", ""]),
            ],
        ),
        SubjectWithGroups(
            name="Materia B",
            clave="B-101",
            groups=[
                _build_group("G3", "Materia B", "B-101", ["07:00-08:30", "", "", "", ""]),
                _build_group("G4", "Materia B", "B-101", ["08:30-10:00", "", "", "", ""]),
            ],
        ),
    ]

    result = generate_schedules(subjects, max_results=10)
    assert len(result) == 2
    for scored in result:
        all_slots: set[int] = set()
        for group in scored.groups:
            assert not (group.slots & all_slots)
            all_slots |= group.slots


def test_forward_checking_prunes_branches() -> None:
    """La verificación hacia adelante reduce la cantidad de ramas exploradas."""
    subjects = [
        SubjectWithGroups(
            name="Materia A",
            clave="A-101",
            groups=[
                _build_group("G1", "Materia A", "A-101", ["07:00-08:30", "", "", "", ""]),
                _build_group("G2", "Materia A", "A-101", ["08:30-10:00", "", "", "", ""]),
            ],
        ),
        SubjectWithGroups(
            name="Materia B",
            clave="B-101",
            groups=[
                _build_group("G3", "Materia B", "B-101", ["07:00-08:30", "", "", "", ""]),
                _build_group("G4", "Materia B", "B-101", ["08:30-10:00", "", "", "", ""]),
            ],
        ),
        SubjectWithGroups(
            name="Materia C",
            clave="C-101",
            groups=[
                _build_group("G5", "Materia C", "C-101", ["07:00-08:30", "", "", "", ""]),
                _build_group("G6", "Materia C", "C-101", ["08:30-10:00", "", "", "", ""]),
            ],
        ),
    ]

    calls_with_fc: list[int] = []
    original_backtrack = scheduler_module._backtrack

    def counting_backtrack(subjects, idx, current, occupied, results):
        calls_with_fc.append(1)
        original_backtrack(subjects, idx, current, occupied, results)

    scheduler_module._backtrack = counting_backtrack
    try:
        generate_schedules(subjects, max_results=10)
    finally:
        scheduler_module._backtrack = original_backtrack

    calls_without_fc: list[int] = []

    def naive_backtrack(subjects, idx, current, occupied, results):
        calls_without_fc.append(1)
        if len(results) >= scheduler_module.MAX_SCHEDULES:
            return
        if idx == len(subjects):
            results.append(current.copy())
            return
        for group in subjects[idx].groups:
            if group.slots & occupied:
                continue
            current.append(group)
            naive_backtrack(subjects, idx + 1, current, occupied | group.slots, results)
            current.pop()

    naive_backtrack(subjects, 0, [], set(), [])

    assert sum(calls_with_fc) < sum(calls_without_fc)


def test_score_compactness_lower_is_better() -> None:
    """Un horario compacto tiene menor puntuación de compacidad."""
    compact = ScoredSchedule(
        groups=[
            _build_group("G1", "A", "A-101", ["07:00-08:30", "", "", "", ""]),
            _build_group("G2", "B", "B-101", ["08:30-10:00", "", "", "", ""]),
        ]
    )
    with_gap = ScoredSchedule(
        groups=[
            _build_group("G1", "A", "A-101", ["07:00-08:30", "", "", "", ""]),
            _build_group("G3", "B", "B-101", ["10:00-11:30", "", "", "", ""]),
        ]
    )

    assert score_compactness(compact.groups) < score_compactness(with_gap.groups)


def test_score_late_start_lower_for_later() -> None:
    """Un horario que inicia más tarde tiene menor puntuación de inicio tardío."""
    early = ScoredSchedule(
        groups=[_build_group("G1", "A", "A-101", ["07:00-08:30", "", "", "", ""])]
    )
    late = ScoredSchedule(
        groups=[_build_group("G2", "A", "A-101", ["10:00-11:30", "", "", "", ""])]
    )

    assert score_late_start(late.groups) < score_late_start(early.groups)


def test_score_free_days_lower_for_more_free_days() -> None:
    """Un horario con más días libres tiene menor puntuación."""
    few_free = ScoredSchedule(
        groups=[
            _build_group("G1", "A", "A-101", ["07:00-08:30", "07:00-08:30", "07:00-08:30", "07:00-08:30", ""]),
        ]
    )
    more_free = ScoredSchedule(
        groups=[
            _build_group("G2", "A", "A-101", ["07:00-08:30", "", "", "", ""]),
        ]
    )

    assert score_free_days(more_free.groups) < score_free_days(few_free.groups)


@pytest.mark.asyncio
async def test_save_and_retrieve_schedule(
    db_session: AsyncSession,
    test_user: User,
) -> None:
    """Se puede guardar un horario y recuperarlo posteriormente."""
    request = SaveScheduleRequest(
        name="Mi horario ideal",
        groups=[
            OptionItemResponse(
                grupo="1AM1",
                clave="MAT-101",
                asignatura="Matemáticas",
                profesor="Profesor A",
                edificio="1",
                aula="101",
                lunes="07:00-08:30",
                martes=None,
                miercoles=None,
                jueves=None,
                viernes=None,
            )
        ],
    )

    saved = await schedule_service.save_schedule(db_session, test_user, request)
    assert saved.name == "Mi horario ideal"
    assert len(saved.groups) == 1
    assert saved.groups[0].grupo == "1AM1"

    schedules = await schedule_service.get_saved_schedules(db_session, test_user)
    assert len(schedules) == 1
    assert schedules[0].id == saved.id


@pytest.mark.asyncio
async def test_toggle_favorite(
    db_session: AsyncSession,
    test_user: User,
) -> None:
    """El endpoint de favorito alterna correctamente el estado."""
    request = SaveScheduleRequest(
        name="Horario favorito",
        groups=[
            OptionItemResponse(
                grupo="1AM1",
                clave="MAT-101",
                asignatura="Matemáticas",
                profesor="Profesor A",
            )
        ],
    )

    saved = await schedule_service.save_schedule(db_session, test_user, request)
    assert saved.is_favorite is False

    toggled = await schedule_service.toggle_favorite(db_session, test_user, saved.id)
    assert toggled.is_favorite is True

    toggled_again = await schedule_service.toggle_favorite(db_session, test_user, saved.id)
    assert toggled_again.is_favorite is False


@pytest.mark.asyncio
async def test_delete_saved_schedule(
    db_session: AsyncSession,
    test_user: User,
) -> None:
    """Se puede eliminar un horario guardado."""
    request = SaveScheduleRequest(
        name="Horario temporal",
        groups=[
            OptionItemResponse(
                grupo="1AM1",
                clave="MAT-101",
                asignatura="Matemáticas",
                profesor="Profesor A",
            )
        ],
    )

    saved = await schedule_service.save_schedule(db_session, test_user, request)
    await schedule_service.delete_saved_schedule(db_session, test_user, saved.id)

    schedules = await schedule_service.get_saved_schedules(db_session, test_user)
    assert len(schedules) == 0


@pytest.mark.asyncio
async def test_cannot_delete_foreign_schedule(
    db_session: AsyncSession,
    test_user: User,
    test_user_2: User,
) -> None:
    """Un usuario no puede eliminar el horario guardado de otro usuario."""
    request = SaveScheduleRequest(
        name="Horario ajeno",
        groups=[
            OptionItemResponse(
                grupo="1AM1",
                clave="MAT-101",
                asignatura="Matemáticas",
                profesor="Profesor A",
            )
        ],
    )

    saved = await schedule_service.save_schedule(db_session, test_user, request)

    with pytest.raises(Exception):  # noqa: B017
        await schedule_service.delete_saved_schedule(db_session, test_user_2, saved.id)
