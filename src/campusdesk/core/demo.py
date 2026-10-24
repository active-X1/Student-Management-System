"""Sample data, so a fresh install has something to look at (``--demo``)."""

from __future__ import annotations

from campusdesk.core.service import StudentService

SAMPLE = [
    ("Amara Okafor", 20, "Computer Science"),
    ("Daniel Mensah", 22, "Mechanical Engineering"),
    ("Fatima Bello", 19, "Medicine"),
    ("Chinedu Eze", 21, "Computer Science"),
    ("Grace Adeyemi", 18, "Law"),
    ("Ibrahim Musa", 23, "Business Administration"),
    ("Joy Nwosu", 20, "Medicine"),
    ("Samuel Danjuma", 24, "Architecture"),
]


def seed_demo(service: StudentService) -> int:
    """Add sample students only when the store is empty. Returns how many were added."""
    if service.count():
        return 0
    for name, age, course in SAMPLE:
        service.add_student(name, age, course)
    return len(SAMPLE)
