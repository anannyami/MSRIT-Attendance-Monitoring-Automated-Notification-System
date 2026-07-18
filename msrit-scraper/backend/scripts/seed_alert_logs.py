from random import choice, randint, uniform
from datetime import datetime, timedelta

from sqlalchemy import text

from backend.database import SessionLocal
from backend.models import Student, AttendanceRecord

db = SessionLocal()

print("Deleting existing alert logs...")

db.execute(text("DELETE FROM alert_logs"))
db.commit()

students = db.query(Student).all()

statuses = [
    "SUCCESS",
    "FAILED",
    "PARTIAL"
]

recipient_types = [
    "STUDENT",
    "TEACHER"
]

records = []

for i in range(1000):

    student = choice(students)

    attendance = (
        db.query(AttendanceRecord)
        .filter(AttendanceRecord.student_id == student.id)
        .first()
    )

    if attendance:
        subject = attendance.subject_name
        percentage = float(attendance.attendance_percentage)
    else:
        subject = "Operating Systems"
        percentage = round(uniform(45, 74), 2)

    status = choice(statuses)

    error = None

    if status == "FAILED":
        error = choice([
            "SMTP timeout",
            "Invalid email",
            "Mailbox unavailable",
            "Temporary server failure"
        ])

    teacher_email = (
        student.teacher.email
        if student.teacher and student.teacher.email
        else "teacher@msrit.edu"
    )

    created = datetime.now() - timedelta(
        days=randint(0, 30),
        hours=randint(0, 23),
        minutes=randint(0, 59),
    )

    records.append({
        "teacher_email": teacher_email,
        "student_name": student.name,
        "usn": student.usn,
        "subject_name": subject,
        "attendance_percentage": percentage,
        "status": status,
        "error_message": error,
        "recipient_type": choice(recipient_types),
        "created_at": created,
    })

db.execute(
    text("""
    INSERT INTO alert_logs
    (
        teacher_email,
        student_name,
        usn,
        subject_name,
        attendance_percentage,
        status,
        error_message,
        recipient_type,
        created_at
    )
    VALUES
    (
        :teacher_email,
        :student_name,
        :usn,
        :subject_name,
        :attendance_percentage,
        :status,
        :error_message,
        :recipient_type,
        :created_at
    )
    """),
    records
)

db.commit()

print(f"Inserted {len(records)} alert logs")

db.close()