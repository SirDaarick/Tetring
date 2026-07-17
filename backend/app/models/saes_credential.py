"""Modelo de credenciales SAES vinculadas a un usuario.

Almacena los tokens de sesión del SAES cifrados con AES-256-GCM. La relación
con `users` es uno a uno: cada cuenta puede tener a lo sumo una boleta
vinculada, y cada boleta pertenece a una sola cuenta.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, LargeBinary, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.user import User


class SaesCredential(Base):
    """Credenciales cifradas del SAES para un usuario específico."""

    __tablename__ = "saes_credentials"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único de la credencial",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
        comment="Usuario propietario de la credencial (relación 1:1)",
    )
    boleta: Mapped[str] = mapped_column(
        String(20),
        unique=True,
        nullable=False,
        comment="Boleta del alumno en el SAES",
    )
    school: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Identificador del plantel (ej. escom, esiatec)",
    )
    encrypted_login: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
        comment="Token `login` del SAES cifrado con AES-256-GCM",
    )
    encrypted_session: Mapped[bytes] = mapped_column(
        LargeBinary,
        nullable=False,
        comment="Token `session` del SAES cifrado con AES-256-GCM",
    )
    saes_expires_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        comment="Fecha de expiración reportada por el SAES",
    )
    last_sync_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        comment="Fecha de la última sincronización académica exitosa",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        comment="Fecha y hora de creación del vínculo",
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
        back_populates="saes_credential",
        uselist=False,
    )


User.saes_credential = relationship(
    "SaesCredential",
    back_populates="user",
    uselist=False,
    cascade="all, delete-orphan",
)
