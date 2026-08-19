"""Modelo de horario guardado por el usuario.

Un horario guardado puede marcarse como favorito y contiene múltiples
opciones de grupo almacenadas en la tabla ``option_items``.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.user import User


class SavedSchedule(Base):
    """Horario guardado por el usuario."""

    __tablename__ = "saved_schedules"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único del horario guardado",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Usuario propietario del horario",
    )
    name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Nombre descriptivo del horario",
    )
    is_favorite: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="Indica si el horario es favorito",
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

    user: Mapped[User] = relationship("User", back_populates="saved_schedules")
    option_items: Mapped[list["OptionItem"]] = relationship(
        "OptionItem",
        back_populates="saved_schedule",
        cascade="all, delete-orphan",
        lazy="selectin",
        order_by="OptionItem.order_index",
    )
