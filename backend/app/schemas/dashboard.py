"""Esquemas Pydantic para el dashboard académico del usuario.

Todos los modelos, descripciones y mensajes están en español (México).
"""

from pydantic import BaseModel, ConfigDict, Field


class KardexEntryResponse(BaseModel):
    """Entrada individual del kárdex del usuario."""

    model_config = ConfigDict(from_attributes=True)

    clave: str = Field(..., description="Clave de la asignatura")
    asignatura: str = Field(..., description="Nombre de la asignatura")
    calificacion: str = Field(..., description="Calificación alfanumérica")
    periodo: str = Field(..., description="Periodo escolar cursado")
    fecha: str | None = Field(None, description="Fecha de acreditación")
    forma_evaluacion: str | None = Field(
        None,
        description="Forma de evaluación (ordinario, extraordinario, etc.)",
    )


class PendingSubjectResponse(BaseModel):
    """Asignatura pendiente por cursar, calculada a partir de la currícula."""

    clave: str = Field(..., description="Clave de la asignatura")
    nombre: str = Field(..., description="Nombre de la asignatura")
    creditos: str | None = Field(None, description="Créditos de la asignatura")
    periodo_curricular: str | None = Field(
        None,
        description="Periodo curricular recomendado",
    )
    semestre: int = Field(0, description="Alias numérico del periodo para el frontend")
    tipo: str | None = Field(None, description="Tipo de asignatura (Obligatoria, Optativa, etc.)")


class PendingBySemester(BaseModel):
    """Agrupación de materias pendientes por periodo curricular."""

    periodo: str = Field(..., description="Periodo curricular")
    materias: int = Field(..., description="Cantidad de materias pendientes")


class CitaReinscripcionInfo(BaseModel):
    """Información de la cita de reinscripción y límites de créditos."""

    fecha: str | None = Field(None, description="Fecha de la cita (ej. 20/08/2026)")
    hora: str | None = Field(None, description="Hora de la cita (ej. 10:30)")
    lugar: str | None = Field(None, description="Lugar o modalidad de la cita")
    estatus: str | None = Field(None, description="Estatus académico (Regular / Irregular)")
    creditos_maximos: str | None = Field(None, description="Créditos máximos permitidos a inscribir")
    creditos_minimos: str | None = Field(None, description="Créditos mínimos permitidos a inscribir")
    mensaje: str | None = Field(None, description="Mensaje informativo del SAES")


class DashboardSummaryResponse(BaseModel):
    """Resumen consolidado del dashboard académico."""

    total_cursadas: int = Field(..., description="Total de asignaturas en el kárdex")
    promedio_general: float | None = Field(
        None,
        description="Promedio general (calificaciones numéricas válidas)",
    )
    creditos_completados: int | None = Field(
        None,
        description="Suma de créditos de materias aprobadas",
    )
    materias_pendientes: int = Field(
        ...,
        description="Cantidad de materias del plan aún no cursadas",
    )
    pending_by_semester: list[PendingBySemester] = Field(
        ...,
        description="Materias pendientes agrupadas por periodo",
    )
    tiene_horario_actual: bool = Field(
        ...,
        description="Indica si el usuario tiene un horario sincronizado",
    )
    
    # Compatibilidad con el Frontend
    cursadas: int | None = Field(None, description="Alias para total_cursadas")
    promedio: float | None = Field(None, description="Alias para promedio_general")
    pendientes: int | None = Field(None, description="Alias para materias_pendientes")
    obligatorias_pendientes: int = Field(0, description="Cantidad de materias obligatorias pendientes")
    optativas_pendientes: int = Field(0, description="Cantidad de materias optativas/electivas restantes por cursar")
    cita: CitaReinscripcionInfo | None = Field(None, description="Cita de reinscripción y créditos")
    last_sync_at: str | None = Field(None, description="Fecha de última sincronización con SAES")


class CurrentScheduleResponse(BaseModel):
    """Grupo inscrito en el horario actual del usuario."""

    model_config = ConfigDict(from_attributes=True)

    grupo: str = Field(..., description="Grupo asignado")
    clave: str = Field(..., description="Clave de la asignatura")
    asignatura: str = Field(..., description="Nombre de la asignatura")
    profesor: str = Field(..., description="Nombre del profesor")
    lunes: str | None = Field(None, description="Horario del lunes")
    martes: str | None = Field(None, description="Horario del martes")
    miercoles: str | None = Field(None, description="Horario del miércoles")
    jueves: str | None = Field(None, description="Horario del jueves")
    viernes: str | None = Field(None, description="Horario del viernes")


class SyncResultResponse(BaseModel):
    """Resultado de una sincronización académica completa."""

    kardex: int = Field(..., description="Entradas de kárdex sincronizadas")
    curriculum: int = Field(..., description="Asignaturas de currícula sincronizadas")
    horario: int = Field(..., description="Grupos del horario actual sincronizados")
