import tkinter as tk

class Management(tk.Tk):
    def __init__(self):
        super().__init__()
        self.students = {}
        self.student_id = 1
        self.header = tk.Label(self, text='SCHOOL MANAGEMENT SYSTEM')
        self.header.pack(pady=50)

        self.add_btn = tk.Button(self, text='Add Students', command=self.add_student, width=20)
        self.add_btn.pack(pady=5)

        self.view_btn = tk.Button(self, text='View Students', command=self.view_students, width=20)
        self.view_btn.pack(pady=5)

        self.search_btn = tk.Button(self, text='Search Student', command=self.search_student, width=20)
        self.search_btn.pack(pady=5)

        self.update_btn = tk.Button(self, text='Update Student', command=self.update_student, width=20)
        self.update_btn.pack(pady=5)

        self.delete_btn = tk.Button(self, text='Delete Student', command=self.delete_student, width=20)
        self.delete_btn.pack(pady=5)

        self.total_btn = tk.Button(self, text='Total Students', command=self.total_students, width=20)
        self.total_btn.pack(pady=5)

        self.exit_btn = tk.Button(self, text='Exit', command=self.destroy, width=10)
        self.exit_btn.pack(pady=50)
        self.congrats = tk.Label(self, text='')
        self.congrats.pack()
        
    def add_student(self):
        self.add_window = tk.Toplevel(self)
        self.add_window.title("Add Student")

        tk.Label(self.add_window, text="Enter student's name: ").pack()
        self.name = tk.Entry(self.add_window)
        self.name.pack()

        tk.Label(self.add_window, text="Enter student's age: ").pack()
        self.age = tk.Entry(self.add_window)
        self.age.pack()

        tk.Label(self.add_window, text="Enter desired course: ").pack()
        self.course = tk.Entry(self.add_window)
        self.course.pack()

        tk.Button(self.add_window, text="Add", command=self.save_student).pack()

    def save_student(self):
        self.students[self.student_id] = {
            "Name": self.name.get(),
            "Age": self.age.get(),
            "Course": self.course.get()
        }
        self.congrats.configure(text=f"Student added successfully! ID: {self.student_id}")
        self.student_id += 1
        self.add_window.destroy()

    def view_students(self):
        self.view_window = tk.Toplevel(self)
        self.view_window.title("Students")
        if not self.students:
            tk.Label(self.view_window, text="No students found.").pack()
            return
        for student_id, student in self.students.items():
            tk.Label(self.view_window, text=f"ID: {student_id}").pack()
            tk.Label(self.view_window, text=f"Name: {student['Name']}").pack()
            tk.Label(self.view_window, text=f"Age: {student['Age']}").pack()
            tk.Label(self.view_window, text=f"Course: {student['Course']}").pack()
            tk.Label(self.view_window, text='-------------------------------').pack()

    def search_student(self):
        self.search_window = tk.Toplevel(self)
        self.search_window.title("Search Student")
        tk.Label(self.search_window, text="Enter student's name: ").pack()
        self.search_name = tk.Entry(self.search_window)
        self.search_name.pack()
        tk.Button(self.search_window, text="Search", command=self.search_result).pack()
        
    def search_result(self):
        search_user = self.search_name.get().lower()
        found = False
        self.result_window = tk.Toplevel(self)
        self.result_window.title("Search Result")
        for student_id, student in self.students.items():
            if student['Name'].lower() == search_user:
                tk.Label(self.result_window, text=f"ID: {student_id}").pack()
                tk.Label(self.result_window, text=f"Name: {student['Name']}").pack()
                tk.Label(self.result_window, text=f"Age: {student['Age']}").pack()
                tk.Label(self.result_window, text=f"Course: {student['Course']}").pack()
                found = True
        if not found:
        	tk.Label(self.result_window, text="Student not found.").pack()
        self.search_window.destroy()

    def update_student(self):
        self.update_window = tk.Toplevel(self)
        self.update_window.title("Update Student")
        tk.Label(self.update_window, text="Enter student ID: ").pack()
        self.update_id = tk.Entry(self.update_window)
        self.update_id.pack()
        tk.Button(self.update_window, text="Next", command=self.update_next).pack()
        self.upd_msg = tk.Label(self.update_window, text='...')
        self.upd_msg.pack()

    def update_next(self):
        try:
            student_id = int(self.update_id.get())
            if student_id in self.students:
                self.update_next_window = tk.Toplevel(self)
                self.update_next_window.title("Update Student")
                tk.Label(self.update_next_window, text="Enter updated name: ").pack()
                self.name = tk.Entry(self.update_next_window)
                self.name.pack()
                tk.Label(self.update_next_window, text="Enter updated age: ").pack()
                self.age = tk.Entry(self.update_next_window)
                self.age.pack()
                tk.Label(self.update_next_window, text="Enter updated course: ").pack()
                self.course = tk.Entry(self.update_next_window)
                self.course.pack()
                tk.Button(self.update_next_window, text="Update", command=lambda: self.save_update(student_id)).pack()
                self.update_window.destroy()
            else:
                self.upd_msg.configure(text="Student not found.")
        except ValueError:
            self.upd_msg.configure(text="Please enter a valid student ID.")

    def save_update(self, student_id):
        self.students[student_id]['Name'] = self.name.get()
        self.students[student_id]['Age'] = self.age.get()
        self.students[student_id]['Course'] = self.course.get()
        self.upd_msg.configure(text="Student updated successfully!")
        self.after(1500, self.update_next_window.destroy)

    def delete_student(self):
        self.delete_window = tk.Toplevel(self)
        self.delete_window.title("Delete Student")
        tk.Label(self.delete_window, text="Enter student ID: ").pack()
        self.delete_id = tk.Entry(self.delete_window)
        self.delete_id.pack()
        tk.Button(self.delete_window, text="Delete", command=self.delete_confirm).pack()
        self.del_msg=tk.Label(self.delete_window, text="...")
        self.del_msg.pack()
        
    def delete_confirm(self):
        try:
            student_id = int(self.delete_id.get())
            if student_id in self.students:
                del self.students[student_id]
                self.del_msg.configure(text="Student deleted successfully!")
                self.after(1500, self.delete_window.destroy)
            else:
                self.del_msg.configure(text="Student not found.")
                
        except ValueError:
            self.del_msg.configure(text="Please enter a valid student ID.")

    def total_students(self):
        total = len(self.students)
        self.total_window = tk.Toplevel(self)
        self.total_window.title("Total Students")
        tk.Label(self.total_window, text=f'There are {total} students in the school.').pack()

root = Management()
root.title('School Portal')
root.geometry('690x1400')
root.mainloop()
