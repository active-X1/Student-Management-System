"""Domain-specific exceptions."""

from __future__ import annotations


class StudentError(Exception):
    """Base class for every error raised by the core."""


class ValidationError(StudentError):
    """Raised when user input is not acceptable. ``field`` names the culprit."""

    def __init__(self, message: str, field: str = "") -> None:
        super().__init__(message)
        self.message = message
        self.field = field


class StudentNotFoundError(StudentError):
    """Raised when a student ID does not exist."""

    def __init__(self, student_id: int) -> None:
        super().__init__(f"No student with ID {student_id}.")
        self.student_id = student_id
