"""Modelo de entradas del kárdex académico de un usuario.

Cada fila representa una asignatura cursada y evaluada en el SAES. Los datos
se sincronizan desde el endpoint `/user/kardex` de `saes-api`.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.user import User


class KardexEntry(Base):
    """Entrada individual del historial académico (kárdex) de un usuario."""

    __tablename__ = "kardex_entries"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único de la entrada",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Usuario propietario de la entrada",
    )
    clave: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Clave de la asignatura en el SAES",
    )
    asignatura: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre completo de la asignatura",
    )
    calificacion: Mapped[str] = mapped_column(
        String(10),
        nullable=False,
        comment="Calificación alfanumérica (ej. 10, 9.5, NP, NA)",
    )
    periodo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Periodo escolar en el que se cursó la asignatura",
    )
    fecha: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="Fecha de acreditación reportada por el SAES",
    )
    forma_evaluacion: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Forma de evaluación (ordinario, extraordinario, etc.)",
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
        back_populates="kardex_entries",
    )

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "clave",
            "periodo",
            name="uq_kardex_entries_user_clave_periodo",
        ),
    )
