"""Menu-driven terminal interface. Works anywhere Python runs."""

from __future__ import annotations

import os
import sys
from typing import Callable, Iterable

from campusdesk import APP_NAME
from campusdesk.core import Student, StudentError, StudentService, ValidationError
from campusdesk.core.validation import validate_age, validate_course, validate_name

MENU = """
 1  Add student
 2  View all students
 3  Search
 4  Update student
 5  Delete student
 6  Statistics
 7  Export to CSV
 0  Exit
"""


def render_table(students: Iterable[Student]) -> str:
    """A tidy, aligned table. Pure function, so it is easy to test."""
    rows = [("ID", "Name", "Age", "Course")] + [(str(s.id), s.name, str(s.age), s.course) for s in students]
    if len(rows) == 1:
        return "  No students found."
    widths = [max(len(r[i]) for r in rows) for i in range(4)]
    def line(r):  # noqa: E306
        return "  " + "  ".join(c.ljust(widths[i]) if i != 2 else c.rjust(widths[i]) for i, c in enumerate(r))
    rule = "  " + "  ".join("─" * w for w in widths)
    return "\n".join([line(rows[0]), rule, *map(line, rows[1:])])


class TerminalApp:
    def __init__(
        self,
        service: StudentService,
        input_fn: Callable[[str], str] | None = None,
        print_fn: Callable[..., None] | None = None,
        color: bool | None = None,
    ) -> None:
        # Look up input()/print() at call time (not definition time) so they can be patched.
        self.service = service
        self.ask = input_fn or (lambda prompt: input(prompt))
        self.say = print_fn or (lambda *args: print(*args))
        self.color = (sys.stdout.isatty() and "NO_COLOR" not in os.environ) if color is None else color

    # ------------------------------------------------------------- helpers
    def paint(self, text: str, code: str) -> str:
        return f"\033[{code}m{text}\033[0m" if self.color else text

    def ok(self, text: str) -> None:
        self.say(self.paint(f"  ✔ {text}", "32"))

    def fail(self, text: str) -> None:
        self.say(self.paint(f"  ✗ {text}", "31"))

    def title(self, text: str) -> None:
        self.say("\n" + self.paint(f"━━ {text} ━━", "1;36"))

    def prompt_valid(self, label: str, validator, current: str | None = None):
        """Keep asking until valid. A blank answer keeps ``current`` when editing."""
        while True:
            hint = f" [{current}]" if current is not None else ""
            raw = self.ask(f"  {label}{hint}: ")
            if current is not None and not raw.strip():
                return validator(current)
            try:
                return validator(raw)
            except ValidationError as err:
                self.fail(err.message)

    def prompt_id(self) -> int | None:
        raw = self.ask("  Student ID: ").strip()
        if not raw.isdigit():
            self.fail("Please enter a valid ID.")
            return None
        return int(raw)

    # ------------------------------------------------------------- actions
    def add(self) -> None:
        self.title("Add student")
        name = self.prompt_valid("Name", validate_name)
        age = self.prompt_valid("Age", validate_age)
        course = self.prompt_valid("Course", validate_course)
        student = self.service.add_student(name, age, course)
        self.ok(f"Added {student.name} with ID {student.id}.")

    def view(self) -> None:
        self.title("Students")
        self.say(render_table(self.service.search()))

    def search(self) -> None:
        self.title("Search")
        query = self.ask("  Name, course or ID: ")
        self.say(render_table(self.service.search(query)))

    def update(self) -> None:
        self.title("Update student")
        sid = self.prompt_id()
        if sid is None:
            return
        try:
            old = self.service.get_student(sid)
        except StudentError as err:
            self.fail(str(err))
            return
        self.say("  Press Enter to keep the current value.")
        name = self.prompt_valid("Name", validate_name, old.name)
        age = self.prompt_valid("Age", validate_age, str(old.age))
        course = self.prompt_valid("Course", validate_course, old.course)
        self.service.update_student(sid, name, age, course)
        self.ok("Student updated.")

    def delete(self) -> None:
        self.title("Delete student")
        sid = self.prompt_id()
        if sid is None:
            return
        try:
            student = self.service.get_student(sid)
        except StudentError as err:
            self.fail(str(err))
            return
        if self.ask(f"  Delete {student.name} (ID {sid})? [y/N]: ").strip().lower() in {"y", "yes"}:
            self.service.delete_student(sid)
            self.ok("Student deleted.")
        else:
            self.say("  Cancelled.")

    def stats(self) -> None:
        self.title("Statistics")
        st = self.service.stats()
        if not st.total:
            self.say("  No students yet.")
            return
        self.say(f"  Students      {st.total}")
        self.say(f"  Courses       {st.course_count}")
        self.say(f"  Average age   {st.average_age_text}")
        self.say("  By course:")
        for course, n in st.by_course.items():
            self.say(f"    {course:<28} {'█' * n} {n}")

    def export(self) -> None:
        self.title("Export")
        path = self.ask("  File name [students.csv]: ").strip() or "students.csv"
        try:
            n = self.service.export_csv(path)
        except OSError as err:
            self.fail(f"Could not write the file: {err}")
            return
        self.ok(f"Exported {n} students to {path}.")

    # ---------------------------------------------------------------- loop
    def run(self) -> int:
        actions = {"1": self.add, "2": self.view, "3": self.search, "4": self.update,
                   "5": self.delete, "6": self.stats, "7": self.export}
        self.say(self.paint(f"\n  🎓 {APP_NAME}", "1;34"))
        try:
            while True:
                self.say(MENU)
                choice = self.ask(" → ").strip()
                if choice in {"0", "q", "exit"}:
                    break
                action = actions.get(choice)
                if action is None:
                    self.fail("Please choose a number from the menu.")
                    continue
                try:
                    action()
                except StudentError as err:
                    self.fail(str(err))
        except (KeyboardInterrupt, EOFError):
            self.say("")
        self.say("  Goodbye!\n")
        return 0


def run(service: StudentService, **_: object) -> int:
    # Some Windows consoles can't print box-drawing characters; degrade instead of crashing.
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(errors="replace")
        except (AttributeError, ValueError):
            pass
    return TerminalApp(service).run()
