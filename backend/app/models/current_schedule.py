"""Modelo del horario actual del usuario en el periodo escolar vigente.

Almacena los grupos en los que el alumno está inscrito actualmente,
sincronizados desde el endpoint `/user/horario` de `saes-api`.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.user import User


class CurrentSchedule(Base):
    """Grupo inscrito en el horario actual del usuario."""

    __tablename__ = "current_schedule"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único del registro de horario",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Usuario propietario del horario",
    )
    grupo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Grupo asignado al usuario para la asignatura",
    )
    clave: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Clave de la asignatura",
    )
    asignatura: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre completo de la asignatura",
    )
    profesor: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre del profesor asignado al grupo",
    )
    lunes: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Horario del lunes (ej. 07:00-08:30)",
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
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha y hora de creación del registro",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha y hora de la última actualización",
    )

    user: Mapped[User] = relationship(
        "User",
        back_populates="current_schedules",
    )
