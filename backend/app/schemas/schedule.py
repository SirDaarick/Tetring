"""Esquemas Pydantic para generación y guardado de horarios.

Todos los modelos, descripciones y mensajes están en español (México).
"""

from datetime import time
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class GenerateRequestFilters(BaseModel):
    """Filtros horarios específicos enviados por el cliente."""
    
    start_min: int | None = Field(None, description="Hora mínima en minutos desde medianoche (ej. 420)")
    start_max: int | None = Field(None, description="Hora máxima en minutos desde medianoche (ej. 1320)")


class GenerateRequest(BaseModel):
    """Solicitud para generar horarios a partir de materias pendientes."""

    subject_claves: list[str] = Field(
        ...,
        description="Claves de asignaturas a incluir en la generación",
    )
    turno: str | None = Field(
        None,
        description="Turno deseado: Matutino, Vespertino o Mixto",
    )
    hora_inicio: time | None = Field(
        None,
        description="Hora mínima de inicio de clases",
    )
    hora_fin: time | None = Field(
        None,
        description="Hora máxima de fin de clases",
    )
    filters: GenerateRequestFilters | None = Field(
        None,
        description="Filtros opcionales de horas específicas",
    )
    pinned_groups: dict[str, str] | None = Field(
        None,
        description="Grupos fijados por materia (clave -> grupo)",
    )
    scoring: list[str] = Field(
        default=["compactness"],
        description="Criterios de puntuación: compactness, late_start, free_days",
    )
    max_results: int = Field(
        default=50,
        ge=1,
        le=500,
        description="Cantidad máxima de resultados a retornar",
    )
    exclude_professors: list[str] | None = Field(
        default=None,
        description="Lista de nombres de profesores a excluir",
    )


class OptionItemResponse(BaseModel):
    """Grupo seleccionado dentro de un horario."""

    model_config = ConfigDict(from_attributes=True)

    grupo: str = Field(..., description="Grupo asignado")
    clave: str = Field(..., description="Clave de la asignatura")
    asignatura: str = Field(..., description="Nombre de la asignatura")
    profesor: str = Field(..., description="Nombre del profesor")
    edificio: str | None = Field(None, description="Edificio")
    aula: str | None = Field(None, description="Aula")
    lunes: str | None = Field(None, description="Horario del lunes")
    martes: str | None = Field(None, description="Horario del martes")
    miercoles: str | None = Field(None, description="Horario del miércoles")
    jueves: str | None = Field(None, description="Horario del jueves")
    viernes: str | None = Field(None, description="Horario del viernes")


class ScheduleResultResponse(BaseModel):
    """Horario generado con sus puntuaciones."""

    index: int = Field(..., description="Índice del resultado ordenado")
    groups: list[OptionItemResponse] = Field(
        ...,
        description="Grupos que componen el horario",
    )
    scores: dict[str, float] = Field(
        ...,
        description="Puntuaciones por criterio",
    )
    total_score: float = Field(
        ...,
        description="Puntuación total normalizada (menor = mejor)",
    )


class GenerateResponse(BaseModel):
    """Respuesta de la generación de horarios."""

    total_generated: int = Field(
        ...,
        description="Total de horarios válidos generados",
    )
    results: list[ScheduleResultResponse] = Field(
        ...,
        description="Horarios puntuados ordenados de mejor a peor",
    )


class SaveScheduleRequest(BaseModel):
    """Solicitud para guardar un horario generado."""

    name: str = Field(..., description="Nombre descriptivo del horario")
    groups: list[OptionItemResponse] = Field(
        ...,
        description="Grupos que componen el horario",
    )


class SavedScheduleResponse(BaseModel):
    """Horario guardado con sus grupos."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Identificador del horario guardado")
    name: str = Field(..., description="Nombre descriptivo del horario")
    is_favorite: bool = Field(..., description="Indica si es favorito")
    groups: list[OptionItemResponse] = Field(
        ...,
        description="Grupos que componen el horario",
    )
    created_at: str | None = Field(
        None,
        description="Fecha de creación en formato ISO",
    )

    @classmethod
    def model_validate(cls, obj: object, **kwargs: object) -> "SavedScheduleResponse":
        """Permite validar desde un modelo ORM convirtiendo created_at a string."""
        data = {}
        if hasattr(obj, "id"):
            data["id"] = obj.id
        if hasattr(obj, "name"):
            data["name"] = obj.name
        if hasattr(obj, "is_favorite"):
            data["is_favorite"] = obj.is_favorite
        if hasattr(obj, "created_at") and obj.created_at is not None:
            data["created_at"] = obj.created_at.isoformat()
        if hasattr(obj, "option_items"):
            data["groups"] = [
                OptionItemResponse.model_validate(item) for item in obj.option_items
            ]
        return super().model_validate(data, **kwargs)
