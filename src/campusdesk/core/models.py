"""Plain data objects shared by every interface."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Student:
    id: int
    name: str
    age: int
    course: str

    @property
    def initials(self) -> str:
        parts = [p for p in self.name.split() if p]
        if not parts:
            return "?"
        if len(parts) == 1:
            return parts[0][:2].upper()
        return (parts[0][0] + parts[-1][0]).upper()

    def matches(self, query: str) -> bool:
        """Case-insensitive match on name or course; a number also matches the ID."""
        q = query.strip().casefold()
        if not q:
            return True
        if q.isdigit() and int(q) == self.id:
            return True
        return q in self.name.casefold() or q in self.course.casefold()


@dataclass(frozen=True)
class Stats:
    total: int = 0
    course_count: int = 0
    average_age: float | None = None
    top_course: str | None = None
    by_course: dict[str, int] = field(default_factory=dict)

    @property
    def average_age_text(self) -> str:
        return "–" if self.average_age is None else f"{self.average_age:.1f}"
