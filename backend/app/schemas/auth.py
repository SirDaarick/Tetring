"""Esquemas Pydantic para autenticación y gestión de usuarios.

Todos los mensajes y descripciones están en español (México) para mantener
la coherencia con el resto de la API.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class UserBase(BaseModel):
    """Campos comunes de los esquemas de usuario."""

    email: EmailStr = Field(
        ...,
        description="Correo electrónico válido del usuario",
        examples=["alumno@ipn.mx"],
    )


class UserCreate(UserBase):
    """Datos requeridos para registrar un nuevo usuario con correo y contraseña."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Contraseña con al menos 8 caracteres",
        examples=["secreto123"],
    )
    full_name: str | None = Field(
        default=None,
        max_length=200,
        description="Nombre completo opcional del usuario",
        examples=["Juan Pérez García"],
    )


class UserLogin(UserBase):
    """Credenciales para iniciar sesión con correo y contraseña."""

    password: str = Field(
        ...,
        min_length=8,
        max_length=128,
        description="Contraseña de la cuenta",
        examples=["secreto123"],
    )


class UserResponse(BaseModel):
    """Representación pública de un usuario en las respuestas de la API."""

    model_config = ConfigDict(from_attributes=True)

    id: UUID = Field(..., description="Identificador único de la cuenta")
    email: EmailStr = Field(..., description="Correo electrónico del usuario")
    full_name: str | None = Field(
        default=None,
        description="Nombre completo del usuario",
    )
    is_active: bool = Field(
        default=True,
        description="Indica si la cuenta está activa",
    )
    created_at: datetime = Field(
        ...,
        description="Fecha y hora de creación de la cuenta",
    )


class TokenResponse(BaseModel):
    """Par de tokens JWT emitidos tras un inicio de sesión exitoso."""

    access_token: str = Field(
        ...,
        description="Token de acceso con vigencia de 15 minutos",
    )
    refresh_token: str = Field(
        ...,
        description="Token de refresco con vigencia de 7 días",
    )
    token_type: str = Field(
        default="bearer",
        description="Tipo de token, siempre 'bearer'",
    )


class RefreshRequest(BaseModel):
    """Solicitud para rotar el par de tokens usando un refresh token válido."""

    refresh_token: str = Field(
        ...,
        description="Token de refresco previamente emitido por el servidor",
    )
