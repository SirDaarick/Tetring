"""Modelo de opción de grupo dentro de un horario guardado.

Cada fila representa un grupo seleccionado para una asignatura en un
horario guardado. Se usa como tabla de unión explícita (no JSONB).
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.saved_schedule import SavedSchedule


class OptionItem(Base):
    """Grupo seleccionado dentro de un horario guardado."""

    __tablename__ = "option_items"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único del grupo en el horario",
    )
    schedule_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("saved_schedules.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Horario guardado al que pertenece",
    )
    grupo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Grupo asignado",
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
    profesor: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre del profesor",
    )
    edificio: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Edificio donde se imparte la clase",
    )
    aula: Mapped[str | None] = mapped_column(
        String(100),
        nullable=True,
        comment="Aula donde se imparte la clase",
    )
    lunes: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Horario del lunes",
    )
    martes: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Horario del martes",
    )
    miercoles: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Horario del miércoles",
    )
    jueves: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Horario del jueves",
    )
    viernes: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Horario del viernes",
    )
    order_index: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
        comment="Orden del grupo dentro del horario",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha y hora de creación",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha y hora de la última actualización",
    )

    saved_schedule: Mapped[SavedSchedule] = relationship(
        "SavedSchedule",
        back_populates="option_items",
    )
