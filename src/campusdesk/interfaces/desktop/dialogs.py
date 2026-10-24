"""Modal add/edit dialog."""

from __future__ import annotations

import tkinter as tk
from typing import Callable

from campusdesk.core import Student, StudentError, StudentService, ValidationError
from campusdesk.interfaces.desktop.widgets import RoundedButton
from campusdesk.theme import Theme


class StudentDialog(tk.Toplevel):
    """Collects name, age and course; validates through the service before closing."""

    def __init__(self, parent: tk.Misc, service: StudentService, theme: Theme, family: str,
                 student: Student | None = None,
                 on_saved: Callable[[Student, bool], None] | None = None) -> None:
        super().__init__(parent, bg=theme.surface)
        self.service, self.theme, self.family = service, theme, family
        self.student, self.on_saved = student, on_saved
        self.title("Edit student" if student else "New student")
        self.resizable(False, False)
        self.transient(parent)
        self._fields: dict[str, tk.Entry] = {}

        body = tk.Frame(self, bg=theme.surface, padx=28, pady=24)
        body.pack(fill="both", expand=True)
        tk.Label(body, text="Edit student" if student else "New student", bg=theme.surface, fg=theme.text,
                 font=(family, 18, "bold")).pack(anchor="w")
        tk.Label(body, text="All fields are required.", bg=theme.surface, fg=theme.muted,
                 font=(family, 10)).pack(anchor="w", pady=(2, 14))

        self._add_field(body, "name", "Full name", student.name if student else "")
        self._add_field(body, "age", "Age", str(student.age) if student else "")
        self._add_field(body, "course", "Course", student.course if student else "")
        self._add_suggestions(body)

        self.error = tk.Label(body, text="", bg=theme.surface, fg=theme.danger_hover, font=(family, 10),
                              wraplength=340, justify="left", anchor="w")
        self.error.pack(fill="x", pady=(10, 0))

        buttons = tk.Frame(body, bg=theme.surface)
        buttons.pack(fill="x", pady=(14, 0))
        RoundedButton(buttons, "Save", self.save, fill=theme.primary, hover=theme.primary_hover,
                      bg=theme.surface, font=(family, 11, "bold"), width=120).pack(side="right")
        RoundedButton(buttons, "Cancel", self.destroy, fill=theme.surface_alt, hover=theme.border,
                      bg=theme.surface, font=(family, 11), width=110).pack(side="right", padx=(0, 10))

        self.bind("<Return>", lambda _e: self.save())
        self.bind("<Escape>", lambda _e: self.destroy())
        self._center_over(parent)
        self._fields["name"].focus_set()
        try:
            self.wait_visibility()
            self.grab_set()
        except tk.TclError:
            pass  # some window managers refuse to grab before mapping; the dialog still works

    # ----------------------------------------------------------------- layout
    def _add_field(self, parent: tk.Misc, key: str, label: str, value: str) -> None:
        t = self.theme
        tk.Label(parent, text=label.upper(), bg=t.surface, fg=t.muted, font=(self.family, 9, "bold")).pack(anchor="w", pady=(8, 4))
        entry = tk.Entry(parent, font=(self.family, 13), bg=t.field, fg=t.text, insertbackground=t.primary,
                         relief="flat", bd=0, highlightthickness=1, highlightbackground=t.border,
                         highlightcolor=t.primary, width=34)
        entry.insert(0, value)
        entry.pack(fill="x", ipady=8)
        self._fields[key] = entry

    def _add_suggestions(self, parent: tk.Misc) -> None:
        courses = self.service.courses()[:5]
        if not courses:
            return
        row = tk.Frame(parent, bg=self.theme.surface)
        row.pack(fill="x", pady=(8, 0))
        for course in courses:
            chip = tk.Label(row, text=course, bg=self.theme.surface_alt, fg=self.theme.muted, cursor="hand2",
                            font=(self.family, 9), padx=9, pady=3)
            chip.pack(side="left", padx=(0, 6))
            chip.bind("<Button-1>", lambda _e, c=course: self._use_course(c))
            chip.bind("<Enter>", lambda _e, w=chip: w.configure(fg=self.theme.text))
            chip.bind("<Leave>", lambda _e, w=chip: w.configure(fg=self.theme.muted))

    def _use_course(self, course: str) -> None:
        entry = self._fields["course"]
        entry.delete(0, "end")
        entry.insert(0, course)

    def _center_over(self, parent: tk.Misc) -> None:
        self.update_idletasks()
        w, h = self.winfo_reqwidth(), self.winfo_reqheight()
        x = parent.winfo_rootx() + (parent.winfo_width() - w) // 2
        y = parent.winfo_rooty() + (parent.winfo_height() - h) // 3
        self.geometry(f"+{max(0, x)}+{max(0, y)}")

    # ---------------------------------------------------------------- actions
    def save(self) -> None:
        values = {key: entry.get() for key, entry in self._fields.items()}
        try:
            if self.student is None:
                saved = self.service.add_student(**values)
            else:
                saved = self.service.update_student(self.student.id, **values)
        except ValidationError as err:
            self.error.configure(text=err.message)
            if err.field in self._fields:
                self._fields[err.field].focus_set()
            return
        except StudentError as err:
            self.error.configure(text=str(err))
            return
        created = self.student is None
        self.destroy()
        if self.on_saved:
            self.on_saved(saved, created)
