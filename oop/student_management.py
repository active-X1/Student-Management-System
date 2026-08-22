class Student:
    def __init__(self, name, age, course):
        self.name = name
        self.age = age
        self.course = course

class StudentManagementSystem:
    def __init__(self):
        self.students = {}
        self.student_id = 1

    def add_student(self):
        print('\n========== Adding Student ==========')
        name = input("Enter student's name: ")
        age = input("Enter student's age: ")
        course = input("Enter desired course: ")
        self.students[self.student_id] = Student(name, age, course)
        print(f"Student added successfully! ID: {self.student_id}")
        self.student_id += 1
        print('---------------- Done ---------------\n')

    def view_students(self):
        if not self.students:
            print('\nNo students found.\n')
            return
        print('\n========== Students ==========')
        for student_id, student in self.students.items():
            print(f"ID: {student_id}")
            print(f"Name: {student.name}")
            print(f"Age: {student.age}")
            print(f"Course: {student.course}")
            print('-------------------------------')

    def search_student(self):
        print('\n========== Searching ==========')
        search_user = input("Enter student's name: ").lower()
        found = False
        for student_id, student in self.students.items():
            if student.name.lower() == search_user:
                print(f"\nID: {student_id}")
                print(f"Name: {student.name}")
                print(f"Age: {student.age}")
                print(f"Course: {student.course}")
                print('-------------------------------')
                found = True
        if not found:
            print("Student not found.")

    def update_student(self):
        print('\n========== Update Student ==========')
        try:
            student_id = int(input("Enter student ID: "))
            if student_id in self.students:
                age = input("Enter updated age: ")
                course = input("Enter updated course: ")
                self.students[student_id].age = age
                self.students[student_id].course = course
                print("Student updated successfully!")
            else:
                print("Student not found.")
        except ValueError:
            print("Please enter a valid student ID.")

    def delete_student(self):
        print('\n========== Remove Student ==========')
        try:
            student_id = int(input("Enter student ID: "))
            if student_id in self.students:
                del self.students[student_id]
                print("Student deleted successfully!")
            else:
                print("Student not found.")
        except ValueError:
            print("Please enter a valid student ID.")

    def total_students(self):
        total = len(self.students)
        print('------------ Calculating ----------')
        print(f'\nThere are {total} students in the school.')

    def run(self):
        while True:
            print(''' 
 ========== STUDENTS MANAGEMENT SYSTEM ========== 
 1. Add student
 2. View students
 3. Search student
 4. Update student
 5. Delete student
 6. Total students
 7. Exit 
 ================================================= 
 ''')
            try:
                choice = int(input("-> "))
                if choice == 1:
                    self.add_student()
                elif choice == 2:
                    self.view_students()
                elif choice == 3:
                    self.search_student()
                elif choice == 4:
                    self.update_student()
                elif choice == 5:
                    self.delete_student()
                elif choice == 6:
                    self.total_students()
                elif choice == 7:
                    print("Exiting......")
                    break
                else:
                    print("Invalid input.")
            except ValueError:
                print("Please enter a digit number.")

if __name__ == "__main__":
    system = StudentManagementSystem()
    system.run()
