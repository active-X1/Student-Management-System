students = {}
student_id = 1


def add_students():
    global student_id

    print('\n========== Adding Student ==========')
    name = input("Enter student's name: ")
    age = input("Enter student's age: ")
    course = input("Enter desired course: ")
    students[student_id] = {
        "Name": name,
        "Age": age,
        "Course": course
    }

    print(f"Student added successfully! ID: {student_id}")
    student_id += 1

    print('---------------- Done ---------------\n')


def view_students():
    if not students:
        print('\nNo students found.\n')
        return

    print('\n========== Students ==========')

    for student_id, details in students.items():
        print(f"ID: {student_id}")
        print(f"Name: {details['Name']}")
        print(f"Age: {details['Age']}")
        print(f"Course: {details['Course']}")
        print('-------------------------------')


def search_student():
    print('\n========== Searching ==========')

    search_user = input("Enter student's name: ")

    found = False

    for student_id, details in students.items():

        if details["Name"].lower() == search_user.lower():

            print(f"\nID: {student_id}")
            print(f"Name: {details['Name']}")
            print(f"Age: {details['Age']}")
            print(f"Course: {details['Course']}")
            print('-------------------------------')

            found = True

    if not found:
        print("Student not found.")


def update_student():
    print('\n========== Update Student ==========')
    try:
        student_id = int(input("Enter student ID: "))

        if student_id in students:
            age = input("Enter updated age: ")
            course = input("Enter updated course: ")

            students[student_id]["Age"] = age
            students[student_id]["Course"] = course
            
            print("Student updated successfully!")
        else:
            print("Student not found.")

    except ValueError:
        print("Please enter a valid student ID.")


def delete_student():
    print('\n========== Remove Student ==========')

    try:
        student_id = int(input("Enter student ID: "))
        if student_id in students:
            del students[student_id]
            print("Student deleted successfully!")
        else:
            print("Student not found.")

    except ValueError:
        print("Please enter a valid student ID.")


def total_students():
    total = len(students)

    print('------------ Calculating ----------')
    print(f'\nThere are {total} students in the school.')


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
        enter = int(input("-> "))
        if enter == 1:
            add_students()
        elif enter == 2:
            view_students()
        elif enter == 3:
            search_student()
        elif enter == 4:
            update_student()
        elif enter == 5:
            delete_student()
        elif enter == 6:
            total_students()
        elif enter == 7:
            print("Exiting......")
            break
        else:
            print("Invalid input.")

    except ValueError:
        print("Please enter a digit number.")
