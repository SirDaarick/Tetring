"""Configuración de Alembic para migraciones asíncronas.

Este archivo se ejecuta desde el directorio `backend/`; por eso se añade
`os.path.dirname(os.path.dirname(__file__))` al `sys.path` para poder
importar `app.core.config` y `app.core.database`.
"""

import asyncio
import os
import sys
from logging.config import fileConfig

from alembic import context
from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.core.config import settings
from app.core.database import Base

# Modelos registrados para autogenerar migraciones (se importarán en fases posteriores)
from app.models import (  # noqa: F401
    curriculum_course,
    current_schedule,
    kardex_entry,
    saes_credential,
    user,
)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata


def get_database_url() -> str:
    """Usa DATABASE_URL del entorno para soportar SQLite y PostgreSQL."""
    return settings.DATABASE_URL


def run_migrations_offline() -> None:
    """Ejecuta migraciones en modo offline."""
    url = get_database_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    """Wrapper síncrono requerido por Alembic."""
    context.configure(connection=connection, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Crea el motor async y ejecuta las migraciones."""
    configuration = config.get_section(config.config_ini_section, {})
    configuration["sqlalchemy.url"] = get_database_url()

    connectable = async_engine_from_config(
        configuration,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()


def run_migrations_online() -> None:
    """Punto de entrada para migraciones online."""
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
