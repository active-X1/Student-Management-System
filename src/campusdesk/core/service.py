"""Business logic. Interfaces talk to this class and never to a repository directly."""

from __future__ import annotations

import csv
import io
import json
from collections import Counter
from pathlib import Path

from campusdesk.core.errors import ValidationError
from campusdesk.core.models import Stats, Student
from campusdesk.core.repository import StudentRepository
from campusdesk.core.validation import validate_student

SORT_KEYS = {
    "id": lambda s: s.id,
    "name": lambda s: s.name.casefold(),
    "age": lambda s: (s.age, s.name.casefold()),
    "course": lambda s: (s.course.casefold(), s.name.casefold()),
}


class StudentService:
    def __init__(self, repository: StudentRepository) -> None:
        self.repository = repository

    # ------------------------------------------------------------------ CRUD
    def add_student(self, name: object, age: object, course: object) -> Student:
        return self.repository.add(*validate_student(name, age, course))

    def update_student(self, student_id: int, name: object, age: object, course: object) -> Student:
        return self.repository.update(student_id, *validate_student(name, age, course))

    def delete_student(self, student_id: int) -> Student:
        student = self.repository.get(student_id)
        self.repository.delete(student_id)
        return student

    def get_student(self, student_id: int) -> Student:
        return self.repository.get(student_id)

    # --------------------------------------------------------------- queries
    def search(self, query: str = "", sort_by: str = "id", descending: bool = False) -> list[Student]:
        if sort_by not in SORT_KEYS:
            raise ValueError(f"Cannot sort by {sort_by!r}. Choose from: {', '.join(SORT_KEYS)}.")
        found = [s for s in self.repository.all() if s.matches(query)]
        return sorted(found, key=SORT_KEYS[sort_by], reverse=descending)

    def courses(self) -> list[str]:
        """Distinct course names (first spelling wins), alphabetically."""
        seen: dict[str, str] = {}
        for s in self.repository.all():
            seen.setdefault(s.course.casefold(), s.course)
        return sorted(seen.values(), key=str.casefold)

    def count(self) -> int:
        return len(self.repository.all())

    def stats(self) -> Stats:
        students = self.repository.all()
        if not students:
            return Stats()
        counts: Counter[str] = Counter()
        names: dict[str, str] = {}
        for s in students:
            key = s.course.casefold()
            counts[key] += 1
            names.setdefault(key, s.course)
        by_course = {names[k]: n for k, n in sorted(counts.items(), key=lambda kv: (-kv[1], kv[0]))}
        return Stats(
            total=len(students),
            course_count=len(counts),
            average_age=sum(s.age for s in students) / len(students),
            top_course=next(iter(by_course)),
            by_course=by_course,
        )

    # ----------------------------------------------------------- import/export
    def export_csv_text(self) -> str:
        buffer = io.StringIO()
        writer = csv.writer(buffer, lineterminator="\n")
        writer.writerow(["ID", "Name", "Age", "Course"])
        for s in self.search():
            writer.writerow([s.id, s.name, s.age, s.course])
        return buffer.getvalue()

    def export_csv(self, path: str | Path) -> int:
        Path(path).write_text(self.export_csv_text(), encoding="utf-8", newline="")
        return self.count()

    def import_json(self, path: str | Path) -> int:
        """Import records from the original app's ``students.json`` format.

        Accepts ``{"1": {"Name": ..., "Age": ..., "Course": ...}}`` (optionally under a
        ``"students"`` key). Invalid records are skipped. Returns how many were added.
        """
        data = json.loads(Path(path).read_text(encoding="utf-8"))
        records = data.get("students", data) if isinstance(data, dict) else {}
        added = 0
        for key in sorted(records, key=lambda k: (not str(k).isdigit(), int(k) if str(k).isdigit() else 0)):
            record = records[key]
            try:
                self.add_student(record["Name"], record["Age"], record["Course"])
            except (KeyError, TypeError, ValidationError):
                continue
            added += 1
        return added
