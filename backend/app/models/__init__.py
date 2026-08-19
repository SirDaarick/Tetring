"""Importación de modelos para autogeneración de migraciones Alembic.

Todos los modelos deben importarse aquí para que Alembic pueda detectarlos
automáticamente al ejecutar `alembic revision --autogenerate`.
"""

from app.models.curriculum_course import CurriculumCourse
from app.models.current_schedule import CurrentSchedule
from app.models.kardex_entry import KardexEntry
from app.models.option_item import OptionItem
from app.models.room_occupancy import RoomOccupancy
from app.models.saes_credential import SaesCredential
from app.models.saved_schedule import SavedSchedule
from app.models.user import User

__all__ = [
    "CurriculumCourse",
    "CurrentSchedule",
    "KardexEntry",
    "OptionItem",
    "RoomOccupancy",
    "SaesCredential",
    "SavedSchedule",
    "User",
]
