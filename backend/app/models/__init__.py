"""Importación de modelos para autogeneración de migraciones Alembic.

Todos los modelos deben importarse aquí para que Alembic pueda detectarlos
automáticamente al ejecutar `alembic revision --autogenerate`.
"""

from app.models.saes_credential import SaesCredential
from app.models.user import User

__all__ = ["SaesCredential", "User"]
