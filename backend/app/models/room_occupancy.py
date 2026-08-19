"""Modelo de ocupación de grupos escolares.

Almacena los cupos, inscritos y lugares disponibles de cada grupo. Es
información de alcance escolar (no pertenece a un usuario específico) y
se actualiza periódicamente desde el SAES.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Index, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class RoomOccupancy(Base):
    """Ocupación de un grupo específico en el SAES."""

    __tablename__ = "room_occupancy"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único del registro de ocupación",
    )
    carrera: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Carrera a la que pertenece el grupo",
    )
    grupo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Nombre o clave del grupo",
    )
    clave: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Clave de la asignatura",
    )
    asignatura: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre de la asignatura",
    )
    periodo: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Periodo escolar del registro",
    )
    cupo: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Cupo máximo del grupo",
    )
    inscritos: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Cantidad de alumnos inscritos",
    )
    disponibles: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        comment="Lugares disponibles restantes",
    )
    fetched_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha y hora en que se obtuvo el dato del SAES",
    )

    __table_args__ = (
        Index(
            "ix_room_occupancy_lookup",
            "carrera",
            "grupo",
            "clave",
        ),
    )
