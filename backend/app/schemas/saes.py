"""Esquemas Pydantic para la vinculación de credenciales SAES.

Todos los modelos, descripciones y mensajes están en español (México).
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class SchoolResponse(BaseModel):
    """Información de un plantel soportado por Tetring."""

    model_config = ConfigDict(from_attributes=True)

    id: str = Field(..., description="Identificador corto del plantel (ej. escom)")
    name: str = Field(..., description="Nombre completo del plantel")
    url: str = Field(..., description="URL del SAES para el plantel")


class CaptchaResponse(BaseModel):
    """Respuesta al iniciar el flujo de vinculación SAES."""

    credential: str = Field(..., description="Token temporal de sesión de captcha")
    captcha_id: str = Field(..., description="Identificador de la imagen captcha")
    captcha_base64: str = Field(..., description="Imagen captcha codificada en base64")


class SaesLinkStart(BaseModel):
    """Datos requeridos para iniciar la vinculación con SAES."""

    boleta: str = Field(
        ...,
        pattern=r"^\d{10}$",
        description="Boleta de 10 dígitos del alumno",
    )
    school: str = Field(
        ...,
        min_length=1,
        description="Identificador del plantel (ej. escom, esiatec)",
    )


class SaesLoginSubmit(BaseModel):
    """Datos requeridos para completar la vinculación con SAES."""

    password: str = Field(..., min_length=1, description="Contraseña del SAES")
    captcha_solution: str = Field(
        ...,
        min_length=1,
        description="Solución del captcha presentado al usuario",
    )


class SaesProfileResponse(BaseModel):
    """Perfil de la cuenta SAES vinculada al usuario autenticado."""

    boleta: str = Field(..., description="Boleta vinculada")
    school: str = Field(..., description="Plantel del SAES vinculado")
    linked_at: datetime = Field(..., description="Fecha de vinculación")
    last_sync_at: datetime | None = Field(
        None,
        description="Fecha de la última sincronización académica",
    )
