"""Cliente HTTP para comunicarse con el microservicio `saes-api`.

Todas las funciones son asíncronas y usan `httpx.AsyncClient`. El cliente se
comunica con `saes-api` mediante la URL base configurada en `SAES_API_URL` y
rutea la petición al plantel correcto mediante el encabezado `X-SAES-School`.

Para operaciones autenticadas se envían los encabezados personalizados `login`
y `session` (no se usa `Authorization: Bearer`).
"""

import base64
from typing import Any

import httpx
from fastapi import HTTPException, status

from app.core.config import settings

_SCHOOLS: list[dict[str, str]] = [
    {
        "id": "escom",
        "name": "ESCOM - Escuela Superior de Cómputo",
        "url": "https://saes.escom.ipn.mx",
    },
    {
        "id": "esiatec",
        "name": "ESIATEC - Escuela Superior de Ingeniería y Arquitectura",
        "url": "https://saes.esiatec.ipn.mx",
    },
]


def get_all_schools() -> list[dict[str, str]]:
    """Retorna la lista de plantels configurados para la v1 de Tetring."""
    return _SCHOOLS.copy()


def _saes_url(path: str) -> str:
    """Construye una URL completa a partir de la ruta relativa del SAES."""
    base: str = settings.SAES_API_URL.rstrip("/")
    return f"{base}{path}"


def _map_saes_error(response: httpx.Response, context: str = "SAES") -> HTTPException:
    """Convierte errores de `saes-api` en excepciones HTTP con mensajes en español."""
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        return HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales SAES incorrectas",
        )
    if response.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
        return HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="SAES no disponible, intenta más tarde",
        )
    return HTTPException(
        status_code=status.HTTP_502_BAD_GATEWAY,
        detail=f"Error inesperado de {context}: {response.status_code}",
    )


async def get_saes_session(school: str) -> dict[str, Any]:
    """Obtiene un token de captcha y la imagen captcha del SAES.

    Realiza un `GET` a `{SAES_API_URL}/login` enviando el encabezado
    `X-SAES-School` con el identificador del plantel.

    Retorna un diccionario con la forma:
    ```
    {
        "credential": str,
        "captcha": {"id": str, "imageBase64": str},
    }
    ```
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(
                _saes_url("/login"),
                headers={"X-SAES-School": school},
                timeout=30.0,
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="SAES no disponible, intenta más tarde",
            ) from exc

    if response.status_code != status.HTTP_200_OK:
        raise _map_saes_error(response, "captcha")

    return response.json()


async def authenticate_saes(
    school: str,
    credential: str,
    username: str,
    password: str,
    captcha_id: str,
    captcha_solution: str,
) -> dict[str, Any]:
    """Autentica al alumno en el SAES y obtiene los tokens de sesión.

    Realiza un `POST` a `{SAES_API_URL}/login` enviando el encabezado `session`
    con el valor del `credential` temporal y `X-SAES-School` con el plantel.

    Retorna un diccionario con la forma:
    ```
    {"login": str, "session": str, "updateAfter": int | None}
    ```
    """
    payload: dict[str, Any] = {
        "username": username,
        "password": password,
        "captcha": {"id": captcha_id, "solution": captcha_solution},
    }

    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                _saes_url("/login"),
                headers={
                    "X-SAES-School": school,
                    "session": credential,
                },
                json=payload,
                timeout=30.0,
            )
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="SAES no disponible, intenta más tarde",
            ) from exc

    if response.status_code != status.HTTP_200_OK:
        raise _map_saes_error(response, "autenticación SAES")

    return response.json()


async def make_saes_request(
    school: str,
    login_token: str,
    session_token: str,
    path: str,
    method: str = "GET",
) -> dict[str, Any]:
    """Realiza una petición genérica autenticada contra `saes-api`.

    Envía los encabezados `login` y `session` (NO `Authorization: Bearer`).
    Acepta `GET` o `POST`; el cuerpo opcional se pasa como JSON vacío para `POST`.
    """
    url: str = _saes_url(path)
    headers: dict[str, str] = {
        "X-SAES-School": school,
        "login": login_token,
        "session": session_token,
    }

    async with httpx.AsyncClient() as client:
        try:
            if method.upper() == "POST":
                response = await client.post(url, headers=headers, json={}, timeout=30.0)
            else:
                response = await client.get(url, headers=headers, timeout=30.0)
        except httpx.RequestError as exc:
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail="SAES no disponible, intenta más tarde",
            ) from exc

    if response.status_code != status.HTTP_200_OK:
        raise _map_saes_error(response, "SAES")

    return response.json()


def encode_captcha_base64(raw_bytes: bytes) -> str:
    """Codifica la imagen captcha en base64 para mostrarla en el frontend."""
    return base64.b64encode(raw_bytes).decode("ascii")
