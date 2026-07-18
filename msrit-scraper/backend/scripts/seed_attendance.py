
from datetime import datetime, UTC, timedelta
import random
from backend.database import SessionLocal
from backend.models import Student, AttendanceRecord

SUBJECTS=[
    ("Data Structures","Theory"),
    ("Operating Systems","Theory"),
    ("Database Management Systems","Theory"),
    ("Computer Networks","Theory"),
    ("Java Programming Lab","Lab"),
    ("Python Programming","Theory"),
    ("Artificial Intelligence","Theory"),
    ("Cloud Computing","Theory"),
]
SCRAPE_DAYS=3

db=SessionLocal()
try:
    db.query(AttendanceRecord).delete()
    db.commit()
    students=db.query(Student).all()
    rows=[]
    now=datetime.now(UTC)
    for day in range(SCRAPE_DAYS):
        scrape_time=now-timedelta(days=day)
        for student in students:
            for subject,ctype in SUBJECTS:
                total=random.randint(28,60)
                pct=round(random.uniform(45.0,100.0),2)
                attended=round((pct/100)*total)
                rows.append(
                    AttendanceRecord(
                        student_id=student.id,
                        subject_name=subject,
                        course_type=ctype,
                        attendance_percentage=pct,
                        total_classes=total,
                        attended_classes=attended,
                        cie_max_marks=50,
                        cie_obtained_marks=random.randint(20,50),
                        scraped_at=scrape_time,
                    )
                )
    db.bulk_save_objects(rows)
    db.commit()
    print(f"Inserted {len(rows)} attendance records.")
finally:
    db.close()
