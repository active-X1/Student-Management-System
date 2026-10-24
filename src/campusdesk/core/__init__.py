"""Pure logic, storage and validation. No UI code lives here."""

from campusdesk.core.demo import seed_demo
from campusdesk.core.errors import StudentError, StudentNotFoundError, ValidationError
from campusdesk.core.models import Stats, Student
from campusdesk.core.paths import default_db_path
from campusdesk.core.repository import MemoryRepository, SqliteRepository, StudentRepository
from campusdesk.core.service import StudentService

__all__ = [
    "MemoryRepository", "SqliteRepository", "Stats", "Student", "StudentError",
    "StudentNotFoundError", "StudentRepository", "StudentService", "ValidationError",
    "default_db_path", "seed_demo",
]
