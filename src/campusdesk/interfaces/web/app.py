"""NiceGUI interface: a responsive dashboard that works in any browser, phones included."""

from __future__ import annotations


from fastapi import Response
from nicegui import app, ui

from campusdesk import APP_NAME, __version__
from campusdesk.core import Student, StudentError, StudentService, ValidationError
from campusdesk.interfaces.web.styles import build_css
from campusdesk.resources import ASSETS as ASSETS_DIR
from campusdesk.theme import THEME, avatar_color, course_color

ASSET_URL = "/cd-assets"
SORTS = (("id", "ID"), ("name", "Name"), ("age", "Age"), ("course", "Course"))
_STATE: dict[str, StudentService | None] = {"service": None}


def _tint(hex_color: str, alpha: float) -> str:
    r, g, b = (int(hex_color[i:i + 2], 16) for i in (1, 3, 5))
    return f"rgba({r},{g},{b},{alpha})"


class StudentsPage:
    """One browser tab. All data lives in the shared service; view state is per tab."""

    def __init__(self, service: StudentService) -> None:
        self.service = service
        self.query = ""
        self.sort_by, self.descending = "id", False
        self.editing_id: int | None = None
        self.pending_delete: Student | None = None

        self.stats_view = ui.refreshable(self._render_stats)
        self.sort_view = ui.refreshable(self._render_sort)
        self.list_view = ui.refreshable(self._render_list)
        self.chart_view = ui.refreshable(self._render_chart)
        self.suggest_view = ui.refreshable(self._render_suggestions)
        self._build()

    # ------------------------------------------------------------------ layout
    def _build(self) -> None:
        ui.dark_mode(True)
        ui.colors(primary=THEME.primary, positive=THEME.success, negative=THEME.danger)
        self._build_dialogs()
        with ui.element("div").classes("cd-shell"):
            with ui.element("div").classes("cd-header"):
                with ui.element("div").classes("cd-brand"):
                    ui.element("img").props(f'src="{ASSET_URL}/logo.svg" alt="{APP_NAME} logo"')
                    with ui.element("div"):
                        ui.label(APP_NAME).classes("cd-title")
                        ui.label("Manage students, courses and records").classes("cd-sub")
                ui.button("+ Add student", on_click=lambda: self.open_form(None)).props("unelevated no-caps color=primary size=md")

            self.stats_view()

            with ui.element("div").classes("cd-toolbar"):
                search = ui.input(placeholder="Search by name, course or ID…", on_change=self._on_search)
                search.props("outlined dense dark clearable debounce=150").classes("cd-search")
                self.sort_view()
                ui.link("Export CSV", "/export.csv").classes("cd-export")

            with ui.element("div").classes("cd-main"):
                self.list_view()
                self.chart_view()

            ui.label(f"{APP_NAME} v{__version__} · built with Python & NiceGUI").classes("cd-footer")

    def _build_dialogs(self) -> None:
        with ui.dialog() as self.form_dialog, ui.card().classes("cd-dialog"):
            self.form_title = ui.label("New student").classes("cd-title").style("font-size:1.4rem")
            self.f_name = ui.input(label="Full name").props("outlined dense dark autofocus").classes("w-full")
            self.f_age = ui.input(label="Age").props("outlined dense dark inputmode=numeric").classes("w-full")
            self.f_course = ui.input(label="Course").props("outlined dense dark").classes("w-full")
            self.suggest_view()
            self.form_error = ui.label("").classes("cd-error")
            with ui.row().classes("w-full justify-end"):
                ui.button("Cancel", on_click=self.form_dialog.close).props("flat no-caps color=grey-5")
                ui.button("Save", on_click=self.save).props("unelevated no-caps color=primary")
            for field in (self.f_name, self.f_age, self.f_course):
                field.on("keydown.enter", self.save)

        with ui.dialog() as self.confirm_dialog, ui.card().classes("cd-dialog"):
            ui.label("Delete student?").classes("cd-title").style("font-size:1.4rem")
            self.confirm_text = ui.label("")
            with ui.row().classes("w-full justify-end"):
                ui.button("Keep", on_click=self.confirm_dialog.close).props("flat no-caps color=grey-5")
                ui.button("Delete", on_click=self.do_delete).props("unelevated no-caps color=negative")

    # --------------------------------------------------------------- renderers
    def _render_stats(self) -> None:
        st = self.service.stats()
        cards = (
            (str(st.total), "Students", THEME.primary, False),
            (str(st.course_count), "Courses", THEME.success, False),
            (st.average_age_text, "Average age", THEME.warning, False),
            (st.top_course or "–", "Most popular", "#a78bfa", True),
        )
        with ui.element("div").classes("cd-stats"):
            for value, caption, accent, small in cards:
                with ui.element("div").classes("cd-stat glass").style(f"--accent:{accent}"):
                    ui.label(value).classes("num small" if small else "num")
                    ui.label(caption).classes("cap")

    def _render_sort(self) -> None:
        with ui.element("div").classes("cd-chips"):
            ui.label("Sort")
            for key, label in SORTS:
                active = key == self.sort_by
                arrow = (" ↓" if self.descending else " ↑") if active else ""
                button = ui.element("button").classes("cd-sort" + (" active" if active else "")).props('type="button"')
                button.on("click", lambda _e, k=key: self.set_sort(k))
                with button:
                    ui.label(label + arrow)

    def _render_list(self) -> None:
        students = self.service.search(self.query, self.sort_by, self.descending)
        with ui.element("div").classes("cd-list glass"):
            if not students:
                with ui.element("div").classes("cd-empty"):
                    ui.element("img").props(f'src="{ASSET_URL}/logo.svg" alt=""')
                    if self.query:
                        ui.label("No matches").classes("big")
                        ui.label(f"Nothing found for “{self.query}”.")
                    else:
                        ui.label("No students yet").classes("big")
                        ui.label("Click “Add student” to create the first record.")
                return
            for index, s in enumerate(students):
                color = course_color(s.course)
                with ui.element("div").classes("cd-row").style(f"animation-delay:{min(index, 12) * 25}ms"):
                    ui.label(s.initials).classes("cd-avatar").style(f"background:{avatar_color(s.name)}")
                    with ui.element("div"):
                        ui.label(s.name).classes("cd-name")
                        with ui.element("div").classes("cd-meta"):
                            ui.label(s.course).classes("cd-chip").style(
                                f"color:{color};border-color:{_tint(color, .45)};background:{_tint(color, .12)}")
                            ui.label(f"Age {s.age}")
                    ui.label(f"#{s.id}").classes("cd-id")
                    with ui.element("div").classes("cd-actions"):
                        ui.button("Edit", on_click=lambda s=s: self.open_form(s)).props("flat dense no-caps color=blue-4")
                        ui.button("Delete", on_click=lambda s=s: self.ask_delete(s)).props("flat dense no-caps color=red-4")

    def _render_chart(self) -> None:
        st = self.service.stats()
        with ui.element("div").classes("cd-chart glass"):
            ui.label("Students by course").classes("cd-chart-title")
            if not st.by_course:
                ui.label("Charts appear once you add students.").classes("cd-sub")
                return
            biggest = max(st.by_course.values())
            for course, n in list(st.by_course.items())[:7]:
                with ui.element("div").classes("cd-bar-row"):
                    with ui.element("div").classes("top"):
                        ui.label(course)
                        ui.label(str(n)).style(f"color:{THEME.muted}")
                    with ui.element("div").classes("cd-bar"):
                        ui.element("div").style(f"width:{n / biggest * 100:.0f}%;background:{course_color(course)}")

    def _render_suggestions(self) -> None:
        with ui.element("div").classes("cd-suggest"):
            for course in self.service.courses()[:6]:
                button = ui.element("button").props('type="button"')
                button.on("click", lambda _e, c=course: setattr(self.f_course, "value", c))
                with button:
                    ui.label(course)

    # ----------------------------------------------------------------- actions
    def refresh_all(self) -> None:
        self.stats_view.refresh()
        self.list_view.refresh()
        self.chart_view.refresh()
        self.suggest_view.refresh()

    def _on_search(self, event) -> None:
        self.query = (event.value or "").strip()
        self.list_view.refresh()

    def set_sort(self, key: str) -> None:
        self.descending = (not self.descending) if key == self.sort_by else False
        self.sort_by = key
        self.sort_view.refresh()
        self.list_view.refresh()

    def open_form(self, student: Student | None) -> None:
        self.editing_id = student.id if student else None
        self.form_title.set_text("Edit student" if student else "New student")
        self.f_name.value = student.name if student else ""
        self.f_age.value = str(student.age) if student else ""
        self.f_course.value = student.course if student else ""
        self.form_error.set_text("")
        self.suggest_view.refresh()
        self.form_dialog.open()

    def save(self, _event=None) -> None:
        try:
            if self.editing_id is None:
                s = self.service.add_student(self.f_name.value, self.f_age.value, self.f_course.value)
                message = f"Added {s.name}"
            else:
                s = self.service.update_student(self.editing_id, self.f_name.value, self.f_age.value, self.f_course.value)
                message = f"Updated {s.name}"
        except ValidationError as err:
            self.form_error.set_text(err.message)
            return
        except StudentError as err:
            self.form_error.set_text(str(err))
            return
        self.form_dialog.close()
        ui.notify(message, type="positive")
        self.refresh_all()

    def ask_delete(self, student: Student) -> None:
        self.pending_delete = student
        self.confirm_text.set_text(f"{student.name} (ID {student.id}) will be removed permanently.")
        self.confirm_dialog.open()

    def do_delete(self) -> None:
        student, self.pending_delete = self.pending_delete, None
        self.confirm_dialog.close()
        if student is None:
            return
        try:
            self.service.delete_student(student.id)
        except StudentError as err:
            ui.notify(str(err), type="negative")
        else:
            ui.notify(f"Deleted {student.name}", type="warning")
        self.refresh_all()


@ui.page("/")
def index() -> None:
    ui.add_css(build_css())
    service = _STATE["service"]
    assert service is not None, "run() must be called before opening the page"
    StudentsPage(service)


def run(service: StudentService, port: int = 8080, open_browser: bool = True, **_: object) -> int:
    """Start the web server (blocks until stopped)."""
    _STATE["service"] = service
    app.add_static_files(ASSET_URL, ASSETS_DIR)

    @app.get("/export.csv")
    def export_csv() -> Response:
        return Response(
            service.export_csv_text(),
            media_type="text/csv",
            headers={"Content-Disposition": 'attachment; filename="students.csv"'},
        )

    ui.run(title=APP_NAME, favicon=str(ASSETS_DIR / "logo.svg"), port=port,
           show=open_browser, reload=False, dark=True)
    return 0
