"""Punto de entrada de la aplicación FastAPI.

Expone la aplicación con CORS, gestión de ciclo de vida para la base de datos
y el endpoint de salud en `/api/v1/health`.
"""

from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import APIRouter, FastAPI
from fastapi.middleware.cors import CORSMiddleware

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

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:4173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

v1_router: APIRouter = APIRouter(prefix="/api/v1")


@v1_router.get("/health", response_model=dict[str, str])
async def health_check() -> dict[str, str]:
    """Verifica que el servicio está activo y responde en español."""
    return {"estado": "ok", "mensaje": "Servicio disponible"}


app.include_router(v1_router)
