"""Modelo de asignaturas del plan de estudios (currícula) de un usuario.

Estos registros se sincronizan desde el endpoint `/general/asignaturas` de
`saes-api` y representan todas las materias que el alumno debe cursar para
una carrera y plantel determinados.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base
from app.models.user import User


class CurriculumCourse(Base):
    """Asignatura del plan de estudios vinculada a un usuario."""

    __tablename__ = "curriculum_courses"

    id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        comment="Identificador único de la asignatura curricular",
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
        comment="Usuario propietario de la currícula",
    )
    school: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="Plantel al que pertenece la currícula (ej. escom, esiatec)",
    )
    carrera: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        comment="Carrera a la que pertenece la asignatura",
    )
    periodo: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Periodo curricular recomendado (semestre o etapa)",
    )
    clave: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="Clave única de la asignatura dentro del plan de estudios",
    )
    nombre: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
        comment="Nombre completo de la asignatura",
    )
    tipo: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="Tipo de asignatura (Obligatoria, Optativa, etc.)",
    )
    creditos: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        comment="Créditos que aporta la asignatura",
    )
    horas_teoria: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        comment="Horas de teoría por semana",
    )
    horas_practica: Mapped[str | None] = mapped_column(
        String(10),
        nullable=True,
        comment="Horas de práctica por semana",
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
        back_populates="curriculum_courses",
    )

    __table_args__ = (
        Index(
            "ix_curriculum_courses_user_school_carrera",
            "user_id",
            "school",
            "carrera",
        ),
    )
