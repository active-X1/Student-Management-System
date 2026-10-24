"""Input cleaning and validation. One place, so every interface behaves the same."""

from __future__ import annotations

from campusdesk.core.errors import ValidationError

MIN_AGE, MAX_AGE = 3, 100
MAX_NAME, MAX_COURSE = 60, 60


def clean_text(value: object) -> str:
    """Trim and collapse repeated whitespace."""
    return " ".join(str(value).split())


def validate_name(value: object) -> str:
    name = clean_text(value)
    if not name:
        raise ValidationError("Please enter the student's name.", "name")
    if len(name) > MAX_NAME:
        raise ValidationError(f"Name must be {MAX_NAME} characters or fewer.", "name")
    if any(ch.isdigit() for ch in name):
        raise ValidationError("A name should not contain numbers.", "name")
    return name


def validate_age(value: object) -> int:
    text = str(value).strip()
    if not text:
        raise ValidationError("Please enter the student's age.", "age")
    if not text.isdigit():
        raise ValidationError("Age must be a whole number.", "age")
    age = int(text)
    if not MIN_AGE <= age <= MAX_AGE:
        raise ValidationError(f"Age must be between {MIN_AGE} and {MAX_AGE}.", "age")
    return age


def validate_course(value: object) -> str:
    course = clean_text(value)
    if not course:
        raise ValidationError("Please enter a course.", "course")
    if len(course) > MAX_COURSE:
        raise ValidationError(f"Course must be {MAX_COURSE} characters or fewer.", "course")
    return course


def validate_student(name: object, age: object, course: object) -> tuple[str, int, str]:
    """Validate all three fields, raising on the first problem."""
    return validate_name(name), validate_age(age), validate_course(course)
