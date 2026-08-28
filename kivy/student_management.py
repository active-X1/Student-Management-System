import os
import json

from kivy.app import App
from kivy.metrics import dp
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.gridlayout import GridLayout
from kivy.uix.scrollview import ScrollView
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.popup import Popup


FILE = "students.json"

BG = (0.05, 0.08, 0.13, 1)
CARD = (0.10, 0.15, 0.22, 1)
INPUT = (0.14, 0.20, 0.30, 1)

WHITE = (1, 1, 1, 1)
GRAY = (0.65, 0.70, 0.77, 1)

BLUE = (0.20, 0.47, 0.96, 1)
GREEN = (0.10, 0.72, 0.42, 1)
RED = (0.90, 0.25, 0.34, 1)
ORANGE = (0.95, 0.60, 0.10, 1)


class SchoolApp(App):

    def build(self):

        self.title = "School Management"

        Window.clearcolor = BG

        self.students = {}
        self.next_id = 1

        self.load_data()

        main = BoxLayout(
            orientation="vertical",
            padding=dp(10),
            spacing=dp(6)
        )

        main.add_widget(self.make_header())
        main.add_widget(self.make_stats())
        main.add_widget(self.make_search())
        main.add_widget(self.make_list())
        main.add_widget(self.make_menu())

        self.main = main

        self.refresh()

        return main

    # -------------------------
    # JSON
    # -------------------------

    def load_data(self):

        if not os.path.exists(FILE):
            return

        try:

            with open(
                FILE,
                "r",
                encoding="utf-8"
            ) as file:

                data = json.load(file)

            records = data.get("students", data)

            self.students = {
                int(key): value
                for key, value in records.items()
            }

            self.next_id = max(
                self.students,
                default=0
            ) + 1

        except Exception:

            self.students = {}
            self.next_id = 1

    def save_data(self):

        try:

            with open(
                FILE,
                "w",
                encoding="utf-8"
            ) as file:

                json.dump(
                    self.students,
                    file,
                    indent=4
                )

        except Exception:

            self.show_message(
                "Could not save data."
            )

    # -------------------------
    # BASIC WIDGETS
    # -------------------------

    def make_label(
        self,
        text,
        size=11,
        color=WHITE
    ):

        label = Label(
            text=text,
            font_size=dp(size),
            color=color,
            halign="left",
            valign="middle"
        )

        label.bind(
            size=lambda obj, value:
            setattr(
                obj,
                "text_size",
                value
            )
        )

        return label

    def make_button(
        self,
        text,
        color,
        command,
        height=43
    ):

        button = Button(
            text=text,
            size_hint_y=None,
            height=dp(height),
            font_size=dp(10),
            bold=True,
            background_normal="",
            background_color=color,
            color=WHITE
        )

        button.bind(
            on_release=command
        )

        return button

    def make_input(
        self,
        hint="",
        value=""
    ):

        return TextInput(
            hint_text=hint,
            text=value,
            multiline=False,
            size_hint_y=None,
            height=dp(42),
            font_size=dp(11),
            background_color=INPUT,
            foreground_color=WHITE,
            hint_text_color=GRAY,
            cursor_color=WHITE,
            padding=[
                dp(8),
                dp(8)
            ]
        )

    # -------------------------
    # HEADER
    # -------------------------

    def make_header(self):

        box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(60)
        )

        box.add_widget(
            self.make_label(
                "SCHOOL MANAGEMENT",
                18,
                WHITE
            )
        )

        box.add_widget(
            self.make_label(
                "Student Administration System",
                8,
                GRAY
            )
        )

        return box

    # -------------------------
    # STATISTICS
    # -------------------------

    def make_stats(self):

        box = BoxLayout(
            size_hint_y=None,
            height=dp(60),
            spacing=dp(5)
        )

        self.total_label = self.make_label(
            "0",
            15,
            BLUE
        )

        self.course_label = self.make_label(
            "0",
            15,
            GREEN
        )

        self.status_label = self.make_label(
            "EMPTY",
            10,
            ORANGE
        )

        box.add_widget(
            self.stat_box(
                "STUDENTS",
                self.total_label
            )
        )

        box.add_widget(
            self.stat_box(
                "COURSES",
                self.course_label
            )
        )

        box.add_widget(
            self.stat_box(
                "STATUS",
                self.status_label
            )
        )

        return box

    def stat_box(
        self,
        title,
        value
    ):

        box = BoxLayout(
            orientation="vertical",
            padding=dp(3)
        )

        box.add_widget(
            self.make_label(
                title,
                7,
                GRAY
            )
        )

        box.add_widget(value)

        return box

    # -------------------------
    # SEARCH
    # -------------------------

    def make_search(self):

        box = BoxLayout(
            size_hint_y=None,
            height=dp(43),
            spacing=dp(5)
        )

        self.search_input = self.make_input(
            "Search name, course or ID..."
        )

        self.search_input.bind(
            text=self.search_changed
        )

        box.add_widget(
            self.search_input
        )

        box.add_widget(
            self.make_button(
                "CLEAR",
                CARD,
                self.clear_search
            )
        )

        return box

    def search_changed(
        self,
        instance,
        value
    ):

        self.refresh()

    def clear_search(
        self,
        instance
    ):

        self.search_input.text = ""

    # -------------------------
    # STUDENT LIST
    # -------------------------

    def make_list(self):

        self.scroll = ScrollView(
            do_scroll_x=False
        )

        self.student_list = GridLayout(
            cols=1,
            spacing=dp(5),
            size_hint_y=None
        )

        self.student_list.bind(
            minimum_height=
            self.student_list.setter(
                "height"
            )
        )

        self.scroll.add_widget(
            self.student_list
        )

        return self.scroll

    def student_card(
        self,
        sid,
        student
    ):

        box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(70),
            padding=dp(6)
        )

        top = BoxLayout(
            size_hint_y=None,
            height=dp(28)
        )

        name = self.make_label(
            student["Name"],
            11,
            WHITE
        )

        id_label = self.make_label(
            "ID: " + str(sid),
            8,
            BLUE
        )

        id_label.halign = "right"

        top.add_widget(name)
        top.add_widget(id_label)

        bottom = BoxLayout()

        age = self.make_label(
            "Age: " +
            str(student["Age"]),
            8,
            GRAY
        )

        course = self.make_label(
            student["Course"],
            8,
            GREEN
        )

        course.halign = "right"

        bottom.add_widget(age)
        bottom.add_widget(course)

        box.add_widget(top)
        box.add_widget(bottom)

        return box

    def refresh(
        self,
        *args
    ):

        if not hasattr(
            self,
            "student_list"
        ):
            return

        self.student_list.clear_widgets()

        query = (
            self.search_input.text
            .strip()
            .lower()
        )

        found = 0

        for sid, student in self.students.items():

            name = student["Name"].lower()
            course = student["Course"].lower()

            if query:

                if (
                    query not in name
                    and
                    query not in course
                    and
                    query != str(sid)
                ):

                    continue

            self.student_list.add_widget(
                self.student_card(
                    sid,
                    student
                )
            )

            found += 1

        if found == 0:

            self.student_list.add_widget(
                self.make_label(
                    "No students found.",
                    11,
                    GRAY
                )
            )

        courses = set()

        for student in self.students.values():

            courses.add(
                student["Course"].lower()
            )

        self.total_label.text = str(
            len(self.students)
        )

        self.course_label.text = str(
            len(courses)
        )

        if self.students:

            self.status_label.text = "ACTIVE"

        else:

            self.status_label.text = "EMPTY"

    # -------------------------
    # MENU
    # -------------------------

    def make_menu(self):

        box = BoxLayout(
            orientation="vertical",
            size_hint_y=None,
            height=dp(145),
            spacing=dp(5)
        )

        row1 = BoxLayout(
            spacing=dp(5)
        )

        row1.add_widget(
            self.make_button(
                "ADD STUDENT",
                GREEN,
                self.add_student
            )
        )

        row1.add_widget(
            self.make_button(
                "UPDATE",
                BLUE,
                self.update_student
            )
        )

        row2 = BoxLayout(
            spacing=dp(5)
        )

        row2.add_widget(
            self.make_button(
                "DELETE",
                RED,
                self.delete_student
            )
        )

        row2.add_widget(
            self.make_button(
                "TOTAL",
                ORANGE,
                self.show_total
            )
        )

        row3 = BoxLayout(
            spacing=dp(5)
        )

        row3.add_widget(
            self.make_button(
                "REFRESH",
                CARD,
                self.refresh
            )
        )

        box.add_widget(row1)
        box.add_widget(row2)
        box.add_widget(row3)

        return box

    # -------------------------
    # POPUP
    # -------------------------

    def create_popup(
        self,
        title,
        height
    ):

        content = BoxLayout(
            orientation="vertical",
            padding=dp(12),
            spacing=dp(7)
        )

        heading = self.make_label(
            title,
            15,
            WHITE
        )

        heading.size_hint_y = None
        heading.height = dp(32)

        content.add_widget(
            heading
        )

        popup = Popup(
            title="",
            content=content,
            size_hint=(0.92, None),
            height=dp(height),
            background_color=CARD,
            separator_color=BLUE,
            auto_dismiss=False
        )

        return popup, content

    # -------------------------
    # ADD
    # -------------------------

    def add_student(
        self,
        instance
    ):

        popup, content = self.create_popup(
            "ADD STUDENT",
            370
        )

        name = self.make_input(
            "Student name"
        )

        age = self.make_input(
            "Student age"
        )

        course = self.make_input(
            "Course"
        )

        content.add_widget(name)
        content.add_widget(age)
        content.add_widget(course)

        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(43),
            spacing=dp(5)
        )

        buttons.add_widget(
            self.make_button(
                "CANCEL",
                RED,
                lambda x:
                popup.dismiss()
            )
        )

        def save():

            n = name.text.strip()
            a = age.text.strip()
            c = course.text.strip()

            if not n or not a or not c:

                self.show_message(
                    "Please fill all fields."
                )

                return

            if not a.isdigit():

                self.show_message(
                    "Age must contain numbers only."
                )

                return

            sid = self.next_id

            self.students[sid] = {
                "Name": n,
                "Age": a,
                "Course": c
            }

            self.next_id += 1

            self.save_data()
            self.refresh()

            popup.dismiss()

            self.show_message(
                "Student added successfully!\n\n"
                "Student ID: " +
                str(sid)
            )

        buttons.add_widget(
            self.make_button(
                "ADD",
                GREEN,
                lambda x: save()
            )
        )

        content.add_widget(buttons)

        popup.open()

    # -------------------------
    # GET ID
    # -------------------------

    def get_student_id(
        self,
        title,
        function
    ):

        popup, content = self.create_popup(
            title,
            235
        )

        content.add_widget(
            self.make_label(
                "Enter student ID:",
                9,
                GRAY
            )
        )

        entry = self.make_input(
            "Example: 1"
        )

        content.add_widget(entry)

        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(43),
            spacing=dp(5)
        )

        buttons.add_widget(
            self.make_button(
                "CANCEL",
                RED,
                lambda x:
                popup.dismiss()
            )
        )

        def continue_action():

            value = entry.text.strip()

            if not value.isdigit():

                self.show_message(
                    "Please enter a valid ID."
                )

                return

            sid = int(value)

            if sid not in self.students:

                self.show_message(
                    "Student ID not found."
                )

                return

            popup.dismiss()

            function(sid)

        buttons.add_widget(
            self.make_button(
                "CONTINUE",
                BLUE,
                lambda x:
                continue_action()
            )
        )

        content.add_widget(buttons)

        popup.open()

    # -------------------------
    # UPDATE
    # -------------------------

    def update_student(
        self,
        instance
    ):

        if not self.students:

            self.show_message(
                "There are no students."
            )

            return

        self.get_student_id(
            "UPDATE STUDENT",
            self.update_form
        )

    def update_form(
        self,
        sid
    ):

        student = self.students[sid]

        popup, content = self.create_popup(
            "EDIT STUDENT",
            370
        )

        name = self.make_input(
            "Student name",
            student["Name"]
        )

        age = self.make_input(
            "Student age",
            str(student["Age"])
        )

        course = self.make_input(
            "Course",
            student["Course"]
        )

        content.add_widget(name)
        content.add_widget(age)
        content.add_widget(course)

        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(43),
            spacing=dp(5)
        )

        buttons.add_widget(
            self.make_button(
                "CANCEL",
                RED,
                lambda x:
                popup.dismiss()
            )
        )

        def save():

            n = name.text.strip()
            a = age.text.strip()
            c = course.text.strip()

            if not n or not a or not c:

                self.show_message(
                    "Please fill all fields."
                )

                return

            if not a.isdigit():

                self.show_message(
                    "Age must contain numbers only."
                )

                return

            self.students[sid] = {
                "Name": n,
                "Age": a,
                "Course": c
            }

            self.save_data()
            self.refresh()

            popup.dismiss()

            self.show_message(
                "Student updated successfully."
            )

        buttons.add_widget(
            self.make_button(
                "SAVE",
                BLUE,
                lambda x: save()
            )
        )

        content.add_widget(buttons)

        popup.open()

    # -------------------------
    # DELETE
    # -------------------------

    def delete_student(
        self,
        instance
    ):

        if not self.students:

            self.show_message(
                "There are no students."
            )

            return

        self.get_student_id(
            "DELETE STUDENT",
            self.delete_confirm
        )

    def delete_confirm(
        self,
        sid
    ):

        student = self.students[sid]

        popup, content = self.create_popup(
            "CONFIRM DELETE",
            260
        )

        content.add_widget(
            self.make_label(
                "Delete this student?\n\n"
                + student["Name"] +
                "\nID: " +
                str(sid),
                11,
                WHITE
            )
        )

        buttons = BoxLayout(
            size_hint_y=None,
            height=dp(43),
            spacing=dp(5)
        )

        buttons.add_widget(
            self.make_button(
                "CANCEL",
                CARD,
                lambda x:
                popup.dismiss()
            )
        )

        def delete():

            del self.students[sid]

            self.save_data()
            self.refresh()

            popup.dismiss()

            self.show_message(
                "Student deleted successfully."
            )

        buttons.add_widget(
            self.make_button(
                "DELETE",
                RED,
                lambda x:
                delete()
            )
        )

        content.add_widget(buttons)

        popup.open()

    # -------------------------
    # TOTAL
    # -------------------------

    def show_message(
        self,
        message
    ):

        popup, content = self.create_popup(
            "NOTICE",
            250
        )

        text = self.make_label(
            message,
            10,
            WHITE
        )

        text.halign = "center"

        content.add_widget(text)

        content.add_widget(
            self.make_button(
                "OK",
                BLUE,
                lambda x:
                popup.dismiss()
            )
        )

        popup.open()


if __name__ == "__main__":

    SchoolApp().run()
