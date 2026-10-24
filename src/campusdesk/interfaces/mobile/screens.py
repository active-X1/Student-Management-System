"""The two screens: the student list and the add/edit form."""

from __future__ import annotations

from kivy.clock import Clock
from kivy.core.window import Window
from kivy.metrics import dp, sp
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.image import Image
from kivy.uix.label import Label
from kivy.uix.modalview import ModalView
from kivy.uix.screenmanager import Screen
from kivy.uix.scrollview import ScrollView
from kivy.uix.stacklayout import StackLayout
from kivy.utils import escape_markup

from campusdesk import APP_NAME
from campusdesk.core import Student, StudentError, ValidationError
from campusdesk.formatting import truncate
from campusdesk.interfaces.mobile.widgets import (
    MUTED, TEXT, Avatar, Card, Fab, PillButton, RoundedInput, TappableCard, TextLabel,
)
from campusdesk.resources import asset_path
from campusdesk.theme import THEME, avatar_color, course_color, hex_to_rgba

SORTS = (("id", "ID"), ("name", "Name"), ("age", "Age"), ("course", "Course"))
ICON = "icon-256.png"


def _bare(hex_color: str) -> str:
    return hex_color.lstrip("#")


class StatTile(Card):
    def __init__(self, caption: str, accent: str, **kwargs) -> None:
        super().__init__(orientation="vertical", padding=[dp(14), dp(10)], spacing=dp(2), **kwargs)
        self.value = TextLabel(text="0", bold=True, font_size=sp(24), color=hex_to_rgba(accent))
        self.add_widget(self.value)
        self.add_widget(TextLabel(text=caption.upper(), font_size=sp(10), color=MUTED, size_hint_y=None, height=dp(16)))


class StudentRow(TappableCard):
    """One student: avatar, name, course · age, and the ID."""

    def __init__(self, student: Student, **kwargs) -> None:
        super().__init__(orientation="horizontal", size_hint_y=None, height=dp(78),
                         padding=[dp(14), dp(12)], spacing=dp(14), **kwargs)
        self.student = student
        self.add_widget(Avatar(avatar_color(student.name), text=student.initials,
                               pos_hint={"center_y": 0.5}))
        info = BoxLayout(orientation="vertical", spacing=dp(2))
        info.add_widget(TextLabel(text=student.name, bold=True, font_size=sp(16), shorten=True,
                                  shorten_from="right"))
        course = escape_markup(truncate(student.course, 26))
        info.add_widget(TextLabel(
            text=f"[color={_bare(course_color(student.course))}]{course}[/color]  "
                 f"[color={_bare(THEME.muted)}]Age {student.age}[/color]",
            markup=True, font_size=sp(13)))
        self.add_widget(info)
        self.add_widget(TextLabel(text=f"#{student.id}", font_size=sp(12), color=MUTED, size_hint_x=None,
                                  width=dp(40), halign="right"))


class EmptyState(BoxLayout):
    def __init__(self, searching: bool, query: str = "", **kwargs) -> None:
        super().__init__(orientation="vertical", size_hint_y=None, height=dp(260), spacing=dp(10),
                         padding=[0, dp(30)], **kwargs)
        self.add_widget(Image(source=asset_path(ICON), size_hint=(1, None), height=dp(86), opacity=0.95))
        title = "No matches" if searching else "No students yet"
        hint = f"Nothing found for “{query}”." if searching else "Tap the + button to add your first student."
        self.add_widget(Label(text=title, bold=True, font_size=sp(18), color=TEXT, size_hint_y=None, height=dp(28)))
        self.add_widget(Label(text=hint, font_size=sp(14), color=MUTED, size_hint_y=None, height=dp(24)))


class HomeScreen(Screen):
    """Header, stats, search, sort chips, the scrolling list and the + button."""

    def __init__(self, controller, **kwargs) -> None:
        super().__init__(name="home", **kwargs)
        self.ctrl = controller
        self.sort_key, self.descending = "id", False
        self._sort_buttons: dict[str, PillButton] = {}

        root = FloatLayout()
        column = BoxLayout(orientation="vertical", padding=[dp(16), dp(14), dp(16), 0], spacing=dp(12))

        header = BoxLayout(size_hint_y=None, height=dp(56), spacing=dp(12))
        header.add_widget(Image(source=asset_path(ICON), size_hint=(None, 1), width=dp(52)))
        titles = BoxLayout(orientation="vertical")
        titles.add_widget(TextLabel(text=APP_NAME, bold=True, font_size=sp(24)))
        titles.add_widget(TextLabel(text="Students, courses and records", font_size=sp(13), color=MUTED))
        header.add_widget(titles)
        column.add_widget(header)

        stats = BoxLayout(size_hint_y=None, height=dp(80), spacing=dp(10))
        self.tiles = {
            "total": StatTile("Students", THEME.primary),
            "courses": StatTile("Courses", THEME.success),
            "average": StatTile("Avg age", THEME.warning),
        }
        for tile in self.tiles.values():
            stats.add_widget(tile)
        column.add_widget(stats)

        self.search = RoundedInput(hint_text="Search name, course or ID", height=dp(50))
        self.search.input.bind(text=lambda *_: self.refresh())
        column.add_widget(self.search)

        sort_row = BoxLayout(size_hint_y=None, height=dp(40), spacing=dp(8))
        sort_row.add_widget(TextLabel(text="Sort", font_size=sp(13), color=MUTED, size_hint_x=None, width=dp(36)))
        for key, label in SORTS:
            button = PillButton(text=label, font_size=sp(13), height=dp(40), radius=dp(20), bold=False)
            button.bind(on_release=lambda _b, k=key: self.set_sort(k))
            self._sort_buttons[key] = button
            sort_row.add_widget(button)
        column.add_widget(sort_row)

        scroll = ScrollView(bar_width=dp(3), do_scroll_x=False)
        self.list = GridLayout(cols=1, spacing=dp(10), size_hint_y=None, padding=[0, dp(4), 0, dp(110)])
        self.list.bind(minimum_height=self.list.setter("height"))
        scroll.add_widget(self.list)
        column.add_widget(scroll)

        root.add_widget(column)
        fab = Fab(pos_hint={"right": 0.95, "y": 0.035})
        fab.bind(on_release=lambda *_: self.ctrl.open_form(None))
        root.add_widget(fab)
        self.add_widget(root)
        self._style_sort_buttons()

    # --------------------------------------------------------------- behaviour
    def _style_sort_buttons(self) -> None:
        for key, button in self._sort_buttons.items():
            active = key == self.sort_key
            arrow = (" v" if self.descending else " ^") if active else ""  # ASCII: the default font lacks arrows
            button.text = dict(SORTS)[key] + arrow
            button.fill = hex_to_rgba(THEME.primary if active else THEME.surface_alt, 1 if active else 0.85)
            button.fill_down = hex_to_rgba(THEME.primary_hover if active else THEME.border)

    def set_sort(self, key: str) -> None:
        self.descending = (not self.descending) if key == self.sort_key else False
        self.sort_key = key
        self._style_sort_buttons()
        self.refresh()

    def refresh(self) -> None:
        service = self.ctrl.service
        query = self.search.text.strip()
        students = service.search(query, self.sort_key, self.descending)
        stats = service.stats()
        self.tiles["total"].value.text = str(stats.total)
        self.tiles["courses"].value.text = str(stats.course_count)
        self.tiles["average"].value.text = stats.average_age_text
        self.list.clear_widgets()
        if not students:
            self.list.add_widget(EmptyState(bool(query), query))
            return
        for student in students:
            row = StudentRow(student)
            row.bind(on_release=lambda r: self.ctrl.open_form(r.student))
            self.list.add_widget(row)


class FormScreen(Screen):
    """Full-screen add/edit form, with course suggestions and a delete action."""

    def __init__(self, controller, **kwargs) -> None:
        super().__init__(name="form", **kwargs)
        self.ctrl = controller
        self.student: Student | None = None

        outer = BoxLayout(orientation="vertical", padding=[dp(16), dp(14), dp(16), dp(10)], spacing=dp(12))
        top = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(12))
        back = PillButton(text="< Back", size_hint_x=None, width=dp(96), height=dp(48), font_size=sp(15),
                          fill=hex_to_rgba(THEME.surface_alt, 0.9), fill_down=hex_to_rgba(THEME.border))
        back.bind(on_release=lambda *_: self.ctrl.go_home())
        top.add_widget(back)
        self.title = TextLabel(text="New student", bold=True, font_size=sp(22))
        top.add_widget(self.title)
        outer.add_widget(top)

        scroll = ScrollView(do_scroll_x=False, bar_width=dp(3))
        body = BoxLayout(orientation="vertical", size_hint_y=None, spacing=dp(8), padding=[0, dp(6), 0, dp(40)])
        body.bind(minimum_height=body.setter("height"))

        self.name_in = RoundedInput(hint_text="e.g. Amara Okafor")
        self.age_in = RoundedInput(hint_text="e.g. 20", input_filter="int", input_type="number")
        self.course_in = RoundedInput(hint_text="e.g. Computer Science")
        for label, widget in (("FULL NAME", self.name_in), ("AGE", self.age_in), ("COURSE", self.course_in)):
            body.add_widget(TextLabel(text=label, font_size=sp(11), bold=True, color=MUTED, size_hint_y=None,
                                      height=dp(26)))
            body.add_widget(widget)

        self.suggestions = StackLayout(size_hint_y=None, spacing=dp(8))
        self.suggestions.bind(minimum_height=self.suggestions.setter("height"))
        body.add_widget(self.suggestions)

        self.error = TextLabel(text="", font_size=sp(14), color=hex_to_rgba(THEME.danger_hover), size_hint_y=None,
                               height=dp(30), max_lines=2)
        body.add_widget(self.error)

        self.save_btn = PillButton(text="Save student")
        self.save_btn.bind(on_release=lambda *_: self.save())
        body.add_widget(self.save_btn)
        self.delete_btn = PillButton(text="Delete student", fill=hex_to_rgba(THEME.danger, 0.18),
                                     fill_down=hex_to_rgba(THEME.danger, 0.4), color=hex_to_rgba(THEME.danger_hover))
        self.delete_btn.bind(on_release=lambda *_: self.ask_delete())
        body.add_widget(self.delete_btn)

        scroll.add_widget(body)
        outer.add_widget(scroll)
        self.add_widget(outer)

        # Enter moves to the next field, and saves from the last one.
        self.name_in.input.bind(on_text_validate=lambda *_: setattr(self.age_in.input, "focus", True))
        self.age_in.input.bind(on_text_validate=lambda *_: setattr(self.course_in.input, "focus", True))
        self.course_in.input.bind(on_text_validate=lambda *_: self.save())

    # --------------------------------------------------------------- behaviour
    def load(self, student: Student | None) -> None:
        self.student = student
        self.title.text = "Edit student" if student else "New student"
        self.name_in.text = student.name if student else ""
        self.age_in.text = str(student.age) if student else ""
        self.course_in.text = student.course if student else ""
        self.error.text = ""
        self.save_btn.text = "Save changes" if student else "Add student"
        self._show_delete(student is not None)
        self._fill_suggestions()
        if student is None:
            Clock.schedule_once(lambda _dt: setattr(self.name_in.input, "focus", True), 0.45)

    def _show_delete(self, visible: bool) -> None:
        self.delete_btn.opacity = 1 if visible else 0
        self.delete_btn.disabled = not visible
        self.delete_btn.height = dp(52) if visible else 0

    def _fill_suggestions(self) -> None:
        self.suggestions.clear_widgets()
        for course in self.ctrl.service.courses()[:6]:
            chip = PillButton(text=truncate(course, 22), size_hint=(None, None), height=dp(38), font_size=sp(13),
                              bold=False, radius=dp(19), fill=hex_to_rgba(THEME.surface_alt, 0.9),
                              fill_down=hex_to_rgba(THEME.border))
            chip.width = dp(30) + len(chip.text) * dp(7.5)
            chip.bind(on_release=lambda _b, c=course: setattr(self.course_in, "text", c))
            self.suggestions.add_widget(chip)

    def save(self) -> None:
        service = self.ctrl.service
        try:
            if self.student is None:
                saved = service.add_student(self.name_in.text, self.age_in.text, self.course_in.text)
                message = f"Added {saved.name}"
            else:
                saved = service.update_student(self.student.id, self.name_in.text, self.age_in.text,
                                               self.course_in.text)
                message = f"Updated {saved.name}"
        except ValidationError as err:
            self.error.text = err.message
            field = {"name": self.name_in, "age": self.age_in, "course": self.course_in}.get(err.field)
            if field is not None:
                field.input.focus = True
            return
        except StudentError as err:
            self.error.text = str(err)
            return
        self.ctrl.go_home(message)

    def ask_delete(self) -> None:
        if self.student is None:
            return
        student = self.student
        dialog = ModalView(size_hint=(0.88, None), height=dp(220), auto_dismiss=True, background="",
                           background_color=(0, 0, 0, 0), overlay_color=(0, 0, 0, 0.65))
        card = Card(orientation="vertical", padding=dp(20), spacing=dp(10), fill=hex_to_rgba(THEME.surface, 1))
        card.add_widget(TextLabel(text="Delete student?", bold=True, font_size=sp(20)))
        card.add_widget(Label(text=f"{student.name} will be removed permanently.", color=MUTED, font_size=sp(14),
                              halign="left", valign="middle", text_size=(dp(280), None)))
        buttons = BoxLayout(size_hint_y=None, height=dp(52), spacing=dp(10))
        keep = PillButton(text="Keep", fill=hex_to_rgba(THEME.surface_alt), fill_down=hex_to_rgba(THEME.border))
        remove = PillButton(text="Delete", fill=hex_to_rgba(THEME.danger), fill_down=hex_to_rgba(THEME.danger_hover))
        keep.bind(on_release=lambda *_: dialog.dismiss())
        remove.bind(on_release=lambda *_: (dialog.dismiss(), self._delete(student)))
        buttons.add_widget(keep)
        buttons.add_widget(remove)
        card.add_widget(buttons)
        dialog.add_widget(card)
        dialog.open()

    def _delete(self, student: Student) -> None:
        try:
            self.ctrl.service.delete_student(student.id)
        except StudentError as err:
            self.error.text = str(err)
            return
        self.ctrl.go_home(f"Deleted {student.name}", ok=False)
