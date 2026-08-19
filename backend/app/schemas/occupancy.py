"""Esquemas Pydantic para monitoreo de cupos.

Todos los modelos, descripciones y mensajes están en español (México).
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class OccupancyResponse(BaseModel):
    """Estado de cupos de un grupo específico."""

    model_config = ConfigDict(from_attributes=True)

    grupo: str = Field(..., description="Nombre o clave del grupo")
    clave: str = Field(..., description="Clave de la asignatura")
    asignatura: str = Field(..., description="Nombre de la asignatura")
    cupo: int = Field(..., description="Cupo máximo del grupo")
    inscritos: int = Field(..., description="Alumnos inscritos")
    disponibles: int = Field(..., description="Lugares disponibles")
    fetched_at: datetime = Field(..., description="Fecha de la última actualización")
    status: str = Field(
        ...,
        description="Estado de disponibilidad: disponible, bajo, critico, lleno, desconocido",
    )


class OccupancyCheckRequest(BaseModel):
    """Solicitud para verificar cupos de un horario guardado."""

    schedule_id: UUID = Field(..., description="Identificador del horario guardado")


class OccupancyCheckResponse(BaseModel):
    """Respuesta con el estado de cupos de todos los grupos de un horario."""

    schedule_id: UUID = Field(..., description="Identificador del horario consultado")
    groups: list[OccupancyResponse] = Field(
        ...,
        description="Lista de estados de cupos por grupo",
    )
    tiene_riesgo: bool = Field(
        ...,
        description="Indica si algún grupo tiene cupo crítico o lleno",
    )
    resumen: str = Field(..., description="Resumen en español del estado de cupos")


class HeartbeatResponse(BaseModel):
    """Respuesta del heartbeat de ocupación."""

    active: bool = Field(..., description="Indica si la sesión de cupos está activa")
