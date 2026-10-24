"""Storage back ends. Anything implementing ``StudentRepository`` will do."""

from __future__ import annotations

import sqlite3
from abc import ABC, abstractmethod
from pathlib import Path

from campusdesk.core.errors import StudentNotFoundError
from campusdesk.core.models import Student


class StudentRepository(ABC):
    @abstractmethod
    def add(self, name: str, age: int, course: str) -> Student: ...

    @abstractmethod
    def get(self, student_id: int) -> Student: ...

    @abstractmethod
    def update(self, student_id: int, name: str, age: int, course: str) -> Student: ...

    @abstractmethod
    def delete(self, student_id: int) -> None: ...

    @abstractmethod
    def all(self) -> list[Student]: ...

    def close(self) -> None:  # optional
        pass


class MemoryRepository(StudentRepository):
    """Non-persistent store; handy for tests and demos."""

    def __init__(self) -> None:
        self._items: dict[int, Student] = {}
        self._next_id = 1

    def add(self, name: str, age: int, course: str) -> Student:
        student = Student(self._next_id, name, age, course)
        self._items[student.id] = student
        self._next_id += 1
        return student

    def get(self, student_id: int) -> Student:
        try:
            return self._items[student_id]
        except KeyError:
            raise StudentNotFoundError(student_id) from None

    def update(self, student_id: int, name: str, age: int, course: str) -> Student:
        self.get(student_id)
        student = Student(student_id, name, age, course)
        self._items[student_id] = student
        return student

    def delete(self, student_id: int) -> None:
        self.get(student_id)
        del self._items[student_id]

    def all(self) -> list[Student]:
        return list(self._items.values())


class SqliteRepository(StudentRepository):
    """Persistent store backed by a single SQLite file (standard library only)."""

    SCHEMA = """
        CREATE TABLE IF NOT EXISTS students (
            id     INTEGER PRIMARY KEY AUTOINCREMENT,
            name   TEXT    NOT NULL,
            age    INTEGER NOT NULL,
            course TEXT    NOT NULL
        )
    """

    def __init__(self, path: str | Path) -> None:
        self.path = str(path)
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._db = sqlite3.connect(self.path, check_same_thread=False)
        self._db.row_factory = sqlite3.Row
        self._db.execute(self.SCHEMA)
        self._db.commit()

    @staticmethod
    def _to_student(row: sqlite3.Row) -> Student:
        return Student(row["id"], row["name"], row["age"], row["course"])

    def add(self, name: str, age: int, course: str) -> Student:
        cur = self._db.execute(
            "INSERT INTO students (name, age, course) VALUES (?, ?, ?)", (name, age, course)
        )
        self._db.commit()
        return Student(cur.lastrowid, name, age, course)

    def get(self, student_id: int) -> Student:
        row = self._db.execute("SELECT * FROM students WHERE id = ?", (student_id,)).fetchone()
        if row is None:
            raise StudentNotFoundError(student_id)
        return self._to_student(row)

    def update(self, student_id: int, name: str, age: int, course: str) -> Student:
        cur = self._db.execute(
            "UPDATE students SET name = ?, age = ?, course = ? WHERE id = ?",
            (name, age, course, student_id),
        )
        self._db.commit()
        if cur.rowcount == 0:
            raise StudentNotFoundError(student_id)
        return Student(student_id, name, age, course)

    def delete(self, student_id: int) -> None:
        cur = self._db.execute("DELETE FROM students WHERE id = ?", (student_id,))
        self._db.commit()
        if cur.rowcount == 0:
            raise StudentNotFoundError(student_id)

    def all(self) -> list[Student]:
        rows = self._db.execute("SELECT * FROM students ORDER BY id").fetchall()
        return [self._to_student(r) for r in rows]

    def close(self) -> None:
        self._db.close()
