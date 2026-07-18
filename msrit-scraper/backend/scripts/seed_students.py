from datetime import datetime, UTC

from backend.database import SessionLocal
from backend.models import Teacher, Student

# ==========================================================
# CONFIG
# ==========================================================

STUDENTS_PER_TEACHER = 60

SEMESTERS = [
    "SEM03",
    "SEM04",
    "SEM05",
    "SEM06",
    "SEM07",
]

REGISTRATION_STATUS = [
    "Regular",
    "Regular",
    "Regular",
    "Regular",
    "Regular",
]

BACKLOG_STATUS = [
    "No Backlogs",
    "No Backlogs",
    "No Backlogs",
    "No Backlogs",
    "1 Backlog",
]

# ==========================================================

db = SessionLocal()

try:

    # Delete old students
    db.query(Student).delete()
    db.commit()

    teachers = (
        db.query(Teacher)
        .order_by(Teacher.id)
        .all()
    )

    students = []

    usn_counter = 1

    for teacher in teachers:

        for i in range(STUDENTS_PER_TEACHER):

            semester = SEMESTERS[(usn_counter - 1) % len(SEMESTERS)]

            registration = REGISTRATION_STATUS[
                (usn_counter - 1) % len(REGISTRATION_STATUS)
            ]

            backlog = BACKLOG_STATUS[
                (usn_counter - 1) % len(BACKLOG_STATUS)
            ]

            student = Student(

                teacher_id=teacher.id,

                name=f"Student {usn_counter}",

                usn=f"1MS23CS{usn_counter:03d}",

                semester=semester,

                registration_status=registration,

                backlogs_status=backlog,

                student_email=f"student{usn_counter}@msrit.edu",

                created_at=datetime.now(UTC),

            )

            students.append(student)

            usn_counter += 1

    db.bulk_save_objects(students)

    db.commit()

    print(f"✅ Inserted {len(students)} students")

finally:

    db.close()