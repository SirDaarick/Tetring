"""Punto de entrada de la aplicación FastAPI.

Expone la aplicación con CORS, gestión de ciclo de vida para la base de datos
y el endpoint de salud en `/api/v1/health`.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware

from app.api.v1.auth import router as auth_router
from app.api.v1.dashboard import router as dashboard_router
from app.api.v1.occupancy import router as occupancy_router
from app.api.v1.saes import router as saes_router
from app.api.v1.schedules import router as schedules_router
from app.core.config import settings
from app.core.database import engine


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Conecta y desconecta el motor de base de datos al iniciar/detener la app."""
    connection = await engine.connect()
    try:
        yield
    finally:
        await connection.close()
        await engine.dispose()


app: FastAPI = FastAPI(
    title="Tetring API",
    description="API REST para Tetring v2 — generador de horarios escolares.",
    version="2.0.0",
    lifespan=lifespan,
)

# Configurar orígenes permitidos (localhost, Vercel y dominios personalizados)
allowed_origins = [
    origin.strip()
    for origin in settings.CORS_ORIGINS.split(",")
    if origin.strip()
]
if settings.FRONTEND_URL and settings.FRONTEND_URL not in allowed_origins:
    allowed_origins.append(settings.FRONTEND_URL.strip())

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=settings.SECRET_KEY,
)

v1_router: APIRouter = APIRouter(prefix="/api/v1")


@v1_router.get("/health", response_model=dict[str, str])
async def health_check() -> dict[str, str]:
    """Verifica que el servicio está activo y responde en español."""
    return {"estado": "ok", "mensaje": "Servicio disponible"}


app.include_router(v1_router)
app.include_router(auth_router, prefix="/api/v1")
app.include_router(saes_router, prefix="/api/v1")
app.include_router(dashboard_router, prefix="/api/v1")
app.include_router(schedules_router, prefix="/api/v1")
app.include_router(occupancy_router, prefix="/api/v1")
