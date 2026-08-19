"""Rutas de autenticación para registro, inicio de sesión y OAuth de Google.

Todas las respuestas y mensajes de error están en español (México).
"""

import secrets
from typing import Annotated, Any

from authlib.integrations.starlette_client import OAuth
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.config import settings
from app.models.user import User
from app.schemas.auth import (
    RefreshRequest,
    TokenResponse,
    UserCreate,
    UserLogin,
    UserResponse,
)
from app.api.deps import get_db
from app.services.auth_service import (
    authenticate_user,
    create_tokens,
    get_or_create_google_user,
    refresh_access_token,
    register_user,
)

router = APIRouter(prefix="/auth", tags=["autenticación"])

oauth = OAuth()
oauth.register(
    name="google",
    client_id=settings.GOOGLE_CLIENT_ID,
    client_secret=settings.GOOGLE_CLIENT_SECRET,
    server_metadata_url="https://accounts.google.com/.well-known/openid-configuration",
    client_kwargs={
        "scope": "openid email profile",
    },
)


@router.post(
    "/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar un nuevo usuario",
)
async def register(
    user_data: UserCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> User:
    """Crea una cuenta de usuario con correo y contraseña."""
    return await register_user(db, user_data)


@router.post(
    "/login",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Iniciar sesión con correo y contraseña",
)
async def login(
    credentials: UserLogin,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Autentica un usuario y devuelve un par de tokens JWT."""
    user = await authenticate_user(db, credentials)
    return create_tokens(user)


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Rotar tokens de acceso y refresco",
)
async def refresh(
    request_data: RefreshRequest,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> TokenResponse:
    """Emite un nuevo par de tokens a partir de un refresh token válido."""
    return await refresh_access_token(db, request_data.refresh_token)


@router.get(
    "/me",
    response_model=UserResponse,
    status_code=status.HTTP_200_OK,
    summary="Obtener usuario autenticado",
)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """Devuelve la información del usuario autenticado."""
    return current_user


@router.get(
    "/google/login",
    summary="Iniciar flujo de autenticación con Google",
)
async def google_login(request: Request) -> RedirectResponse:
    """Redirige al usuario a la pantalla de consentimiento de Google."""
    state: str = secrets.token_urlsafe(32)
    request.session["oauth_state"] = state
    
    # Construir redirect_uri respetando ngrok / https / proxy
    redirect_uri: str = str(request.url_for("google_callback"))
    # Si viene a través de proxy o ngrok con https pero url_for generó http, forzar https
    proto = request.headers.get("x-forwarded-proto")
    if proto == "https" and redirect_uri.startswith("http://"):
        redirect_uri = "https://" + redirect_uri[len("http://"):]
    elif "ngrok" in redirect_uri and redirect_uri.startswith("http://"):
        redirect_uri = "https://" + redirect_uri[len("http://"):]
        
    print(f"\n[GOOGLE OAUTH DEBUG] redirect_uri enviada a Google: --> {redirect_uri} <--\n")
    return await oauth.google.authorize_redirect(request, redirect_uri, state=state)


@router.get(
    "/google/callback",
    summary="Callback de autenticación con Google",
)
async def google_callback(
    request: Request,
    db: Annotated[AsyncSession, Depends(get_db)],
) -> RedirectResponse:
    """Recibe el código de Google, crea o vincula el usuario y redirige al frontend.

    Incluye los tokens en la URL de redirección como parámetros de consulta.
    """
    expected_state: str | None = request.session.pop("oauth_state", None)
    if expected_state is None or request.query_params.get("state") != expected_state:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solicitud de OAuth no válida",
        )

    token: dict[str, Any] = await oauth.google.authorize_access_token(request)
    user_info: dict[str, Any] = token.get("userinfo", {})

    email: str | None = user_info.get("email")
    google_id: str | None = user_info.get("sub")
    full_name: str | None = user_info.get("name")

    if not email or not google_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se pudo obtener la información de Google",
        )

    user = await get_or_create_google_user(db, google_id, email, full_name)
    tokens: TokenResponse = create_tokens(user)

    frontend_url: str = settings.FRONTEND_URL.rstrip("/")
    redirect_url: str = (
        f"{frontend_url}/auth/callback"
        f"?access_token={tokens.access_token}"
        f"&refresh_token={tokens.refresh_token}"
    )
    return RedirectResponse(url=redirect_url)
