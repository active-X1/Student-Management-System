"""The Kivy application: one window, two screens, built for phones first."""

from __future__ import annotations

from pathlib import Path

from kivy.app import App
from kivy.core.window import Window
from kivy.metrics import dp
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.screenmanager import ScreenManager, SlideTransition

from campusdesk import APP_NAME
from campusdesk.core import SqliteRepository, Student, StudentService
from campusdesk.interfaces.mobile.screens import FormScreen, HomeScreen
from campusdesk.interfaces.mobile.widgets import AuroraBackground, Toast
from campusdesk.theme import THEME, hex_to_rgba

ESCAPE_OR_BACK = 27  # the Android back button reports as key 27, like Esc on desktop


class CampusDeskApp(App):
    title = APP_NAME

    def __init__(self, service: StudentService | None = None, **kwargs) -> None:
        super().__init__(**kwargs)
        self.service = service

    # ----------------------------------------------------------------- build
    def build(self) -> FloatLayout:
        if self.service is None:  # on Android/iOS the database lives in the app's private folder
            self.service = StudentService(SqliteRepository(Path(self.user_data_dir) / "students.db"))
        Window.clearcolor = hex_to_rgba(THEME.background[0])
        Window.softinput_mode = "below_target"   # lift the focused field above the on-screen keyboard
        Window.bind(on_keyboard=self._on_keyboard)

        root = FloatLayout()
        self.background = AuroraBackground()
        root.add_widget(self.background)

        self.manager = ScreenManager(transition=SlideTransition(duration=0.22))
        self.home = HomeScreen(self)
        self.form = FormScreen(self)
        self.manager.add_widget(self.home)
        self.manager.add_widget(self.form)
        root.add_widget(self.manager)

        self.toast = Toast(pos_hint={"center_x": 0.5, "y": 0.04})
        root.add_widget(self.toast)
        self.home.refresh()
        return root

    # ------------------------------------------------------------ navigation
    def open_form(self, student: Student | None) -> None:
        self.form.load(student)
        self.manager.transition.direction = "left"
        self.manager.current = "form"

    def go_home(self, message: str = "", ok: bool = True) -> None:
        Window.release_all_keyboards()
        self.home.refresh()
        self.manager.transition.direction = "right"
        self.manager.current = "home"
        if message:
            self.toast.show(message, ok)

    def _on_keyboard(self, _window, key: int, *_args) -> bool:
        if key == ESCAPE_OR_BACK and self.manager.current == "form":
            self.go_home()
            return True   # handled: don't quit the app
        return False      # on the home screen, let the system close the app

    # ------------------------------------------------------------- lifecycle
    def on_pause(self) -> bool:
        return True       # keep the app alive when it goes to the background on Android

    def on_stop(self) -> None:
        self.background.stop()
        if self.service is not None:
            self.service.repository.close()


def run(service: StudentService | None = None, **_: object) -> int:
    CampusDeskApp(service).run()
    return 0
