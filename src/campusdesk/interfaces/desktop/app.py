"""Main window of the desktop interface."""

from __future__ import annotations

import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from tkinter import font as tkfont

from campusdesk import APP_NAME
from campusdesk.core import Student, StudentError, StudentService
from campusdesk.interfaces.desktop.dialogs import StudentDialog
from campusdesk.interfaces.desktop.widgets import (
    ASSETS, GradientHeader, RoundedButton, SearchEntry, StatCard,
)
from campusdesk.theme import THEME, Theme

COLUMNS = (  # key, label, width, anchor, stretch
    ("id", "ID", 70, "center", False),
    ("name", "Name", 280, "w", True),
    ("age", "Age", 80, "center", False),
    ("course", "Course", 280, "w", True),
)


def pick_font_family(root: tk.Misc, candidates: tuple[str, ...]) -> str:
    installed = set(tkfont.families(root))
    return next((name for name in candidates if name in installed), "TkDefaultFont")


def enable_dpi_awareness() -> None:
    """Crisp text on high-DPI Windows screens; harmless elsewhere."""
    if sys.platform.startswith("win"):
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)
        except Exception:  # noqa: BLE001 - purely cosmetic, never fatal
            pass


class DesktopApp(tk.Tk):
    def __init__(self, service: StudentService, theme: Theme = THEME) -> None:
        super().__init__()
        self.service, self.theme = service, theme
        self.family = pick_font_family(self, theme.font_candidates)
        self.sort_key, self.descending = "id", False
        self._flash_job: str | None = None

        self.title(APP_NAME)
        self.configure(bg=theme.background[0])
        self.minsize(900, 620)
        self._set_icon()
        self._style_widgets()
        self._build()
        self._bind_shortcuts()
        self._center(1060, 740)
        self.refresh()
        self.header.start()
        self.protocol("WM_DELETE_WINDOW", self._on_close)

    # ---------------------------------------------------------------- set-up
    def _set_icon(self) -> None:
        try:
            self._icon = tk.PhotoImage(file=str(ASSETS / "icon-256.png"))
            self.iconphoto(True, self._icon)
        except tk.TclError:
            pass

    def _center(self, width: int, height: int) -> None:
        x = max(0, (self.winfo_screenwidth() - width) // 2)
        y = max(0, (self.winfo_screenheight() - height) // 3)
        self.geometry(f"{width}x{height}+{x}+{y}")

    def _style_widgets(self) -> None:
        t, f = self.theme, self.family
        style = ttk.Style(self)
        style.theme_use("clam")
        style.layout("Campus.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])
        style.configure("Campus.Treeview", background=t.surface, fieldbackground=t.surface, foreground=t.text,
                        rowheight=40, borderwidth=0, relief="flat", font=(f, 11))
        style.configure("Campus.Treeview.Heading", background=t.surface_alt, foreground=t.muted, relief="flat",
                        borderwidth=0, font=(f, 10, "bold"), padding=(12, 9))
        style.map("Campus.Treeview", background=[("selected", t.primary)], foreground=[("selected", "#ffffff")])
        style.map("Campus.Treeview.Heading", background=[("active", t.border)], foreground=[("active", t.text)])
        style.configure("Campus.Vertical.TScrollbar", background=t.border, troughcolor=t.surface,
                        bordercolor=t.surface, lightcolor=t.border, darkcolor=t.border, arrowcolor=t.muted,
                        relief="flat", gripcount=0)
        style.map("Campus.Vertical.TScrollbar", background=[("active", t.primary)])

    def _build(self) -> None:
        t, f, bg = self.theme, self.family, self.theme.background[0]
        self.header = GradientHeader(self, t, f)
        self.header.pack(fill="x")

        body = tk.Frame(self, bg=bg)
        body.pack(fill="both", expand=True, padx=26, pady=(14, 0))

        # Stat cards
        stats = tk.Frame(body, bg=bg)
        stats.pack(fill="x")
        self.cards: dict[str, StatCard] = {}
        for col, (key, caption, accent) in enumerate((
            ("total", "Students", t.primary), ("courses", "Courses", t.success),
            ("average", "Average age", t.warning), ("top", "Most popular", "#a78bfa"),
        )):
            card = StatCard(stats, caption, accent, t, f, bg=bg)
            card.grid(row=0, column=col, sticky="ew", padx=(0 if col == 0 else 7, 0 if col == 3 else 7))
            stats.columnconfigure(col, weight=1, uniform="cards")
            self.cards[key] = card

        # Toolbar
        bar = tk.Frame(body, bg=bg)
        bar.pack(fill="x", pady=(16, 12))
        self.search = SearchEntry(bar, t, f, self._on_search, bg=bg)
        self.search.pack(side="left", fill="x", expand=True, padx=(0, 14))
        small = (f, 10, "bold")
        self.btn_export = RoundedButton(bar, "Export CSV", self.export_csv, fill=t.surface_alt, hover=t.border,
                                        bg=bg, font=small, width=108, height=38)
        self.btn_delete = RoundedButton(bar, "Delete", self.delete_selected, fill=t.danger, hover=t.danger_hover,
                                        bg=bg, font=small, width=84, height=38)
        self.btn_edit = RoundedButton(bar, "Edit", self.edit_selected, fill=t.surface_alt, hover=t.border,
                                      bg=bg, font=small, width=76, height=38)
        self.btn_add = RoundedButton(bar, "+ Add student", self.add_student, fill=t.primary, hover=t.primary_hover,
                                     bg=bg, font=small, width=128, height=38)
        for btn in (self.btn_export, self.btn_delete, self.btn_edit, self.btn_add):
            btn.pack(side="right", padx=(8, 0))

        # Table
        holder = tk.Frame(body, bg=t.border, padx=1, pady=1)
        holder.pack(fill="both", expand=True)
        inner = tk.Frame(holder, bg=t.surface)
        inner.pack(fill="both", expand=True)
        self.tree = ttk.Treeview(inner, columns=[c[0] for c in COLUMNS], show="headings",
                                 selectmode="browse", style="Campus.Treeview")
        for key, label, width, anchor, stretch in COLUMNS:
            self.tree.heading(key, text=label, command=lambda k=key: self.sort_by(k))
            self.tree.column(key, width=width, anchor=anchor, stretch=stretch, minwidth=60)
        self.tree.tag_configure("odd", background=t.surface)
        self.tree.tag_configure("even", background=t.surface_alt)
        scroll = ttk.Scrollbar(inner, orient="vertical", command=self.tree.yview, style="Campus.Vertical.TScrollbar")
        self.tree.configure(yscrollcommand=scroll.set)
        scroll.pack(side="right", fill="y")
        self.tree.pack(side="left", fill="both", expand=True)
        self.tree.bind("<<TreeviewSelect>>", lambda _e: self._update_buttons())
        self.tree.bind("<Double-1>", lambda _e: self.edit_selected())
        self.tree.bind("<Return>", lambda _e: self.edit_selected())
        self.tree.bind("<Delete>", lambda _e: self.delete_selected())

        # Empty-state message (shown over the table when nothing matches)
        self.empty = tk.Label(inner, text="", bg=t.surface, fg=t.muted, font=(f, 12), justify="center")

        # Status bar
        status = tk.Frame(self, bg=bg)
        status.pack(fill="x", padx=26, pady=(8, 10))
        self.status_left = tk.Label(status, text="", bg=bg, fg=t.muted, font=(f, 10))
        self.status_left.pack(side="left")
        self.status_right = tk.Label(status, text="Tip: Ctrl+N adds a student, double-click a row to edit.",
                                     bg=bg, fg=t.muted, font=(f, 10))
        self.status_right.pack(side="right")

    def _bind_shortcuts(self) -> None:
        for sequence, handler in (
            ("<Control-n>", lambda _e: self.add_student()),
            ("<Control-f>", lambda _e: self.search.focus()),
            ("<Control-e>", lambda _e: self.export_csv()),
            ("<Escape>", lambda _e: self.search.clear()),
        ):
            self.bind(sequence, handler)
        for sequence, handler in (("<Command-n>", lambda _e: self.add_student()),
                                  ("<Command-f>", lambda _e: self.search.focus())):
            try:  # the Command key only exists on macOS
                self.bind(sequence, handler)
            except tk.TclError:
                pass

    # ------------------------------------------------------------- rendering
    def refresh(self, select_id: int | None = None) -> None:
        keep = select_id if select_id is not None else self._selected_id()
        students = self.service.search(self.search.query(), self.sort_key, self.descending)
        self.tree.delete(*self.tree.get_children())
        for index, s in enumerate(students):
            self.tree.insert("", "end", iid=str(s.id), values=(s.id, s.name, s.age, s.course),
                             tags=("even" if index % 2 else "odd",))
        if keep is not None and self.tree.exists(str(keep)):
            self.tree.selection_set(str(keep))
            self.tree.see(str(keep))
        self._update_headings()
        self._update_stats(len(students))
        self._update_buttons()
        self._update_empty(students)

    def _update_stats(self, shown: int) -> None:
        st = self.service.stats()
        self.cards["total"].set_value(str(st.total))
        self.cards["courses"].set_value(str(st.course_count))
        self.cards["average"].set_value(st.average_age_text)
        self.cards["top"].set_value(st.top_course or "–", small=True)
        self.status_left.configure(text=f"Showing {shown} of {st.total} students")

    def _update_headings(self) -> None:
        arrow = " ▼" if self.descending else " ▲"
        for key, label, *_ in COLUMNS:
            self.tree.heading(key, text=label + (arrow if key == self.sort_key else ""))

    def _update_empty(self, students: list[Student]) -> None:
        if students:
            self.empty.place_forget()
            return
        query = self.search.query()
        self.empty.configure(text=(f"No students match “{query}”." if query else
                                   "No students yet.\nClick “+ Add student” to create the first record."))
        self.empty.place(relx=0.5, rely=0.45, anchor="center")

    def _update_buttons(self) -> None:
        has_selection = self._selected_id() is not None
        self.btn_edit.set_enabled(has_selection)
        self.btn_delete.set_enabled(has_selection)

    def flash(self, text: str, ok: bool = True) -> None:
        if self._flash_job:
            self.after_cancel(self._flash_job)
        self.status_right.configure(text=text, fg=self.theme.success if ok else self.theme.danger_hover)
        self._flash_job = self.after(4000, lambda: self.status_right.configure(
            text="Tip: Ctrl+N adds a student, double-click a row to edit.", fg=self.theme.muted))

    # --------------------------------------------------------------- actions
    def _selected_id(self) -> int | None:
        selection = self.tree.selection()
        return int(selection[0]) if selection else None

    def _on_search(self, _text: str) -> None:
        self.refresh()

    def sort_by(self, key: str) -> None:
        self.descending = (not self.descending) if key == self.sort_key else False
        self.sort_key = key
        self.refresh()

    def add_student(self) -> None:
        StudentDialog(self, self.service, self.theme, self.family, None, self._saved)

    def edit_selected(self) -> None:
        sid = self._selected_id()
        if sid is None:
            return
        try:
            student = self.service.get_student(sid)
        except StudentError as err:
            self.flash(str(err), ok=False)
            self.refresh()
            return
        StudentDialog(self, self.service, self.theme, self.family, student, self._saved)

    def _saved(self, student: Student, created: bool) -> None:
        self.refresh(select_id=student.id)
        self.flash(f"{'Added' if created else 'Updated'} {student.name}.")

    def delete_selected(self) -> None:
        sid = self._selected_id()
        if sid is None:
            return
        try:
            student = self.service.get_student(sid)
        except StudentError as err:
            self.flash(str(err), ok=False)
            self.refresh()
            return
        if messagebox.askyesno("Delete student", f"Delete {student.name} (ID {student.id})?\nThis cannot be undone.",
                               icon="warning", parent=self):
            self.service.delete_student(sid)
            self.refresh()
            self.flash(f"Deleted {student.name}.")

    def export_csv(self) -> None:
        path = filedialog.asksaveasfilename(parent=self, title="Export students", defaultextension=".csv",
                                            initialfile="students.csv", filetypes=[("CSV file", "*.csv")])
        if not path:
            return
        try:
            count = self.service.export_csv(path)
        except OSError as err:
            self.flash(f"Could not export: {err}", ok=False)
        else:
            self.flash(f"Exported {count} students.")

    def _on_close(self) -> None:
        self.header.stop()
        self.destroy()


def run(service: StudentService, **_: object) -> int:
    enable_dpi_awareness()
    DesktopApp(service).mainloop()
    return 0
