from datetime import datetime
import bcrypt

from backend.database import SessionLocal
from backend.models import Teacher

# ==========================
# CONFIG
# ==========================

NUM_TEACHERS = 15
APP_PASSWORD = "Benchmark@123"
PORTAL_PASSWORD = "Portal@123"

# ==========================

db = SessionLocal()

try:
    # Clear existing benchmark teachers (optional)
    db.query(Teacher).delete()
    db.commit()

    teachers = []

    for i in range(1, NUM_TEACHERS + 1):
        teacher = Teacher(
            name=f"Teacher {i}",
            email=f"teacher{i}@msrit.edu",
            portal_username=f"teacher{i}",
            app_password_hash=bcrypt.hashpw(
                APP_PASSWORD.encode(),
                bcrypt.gensalt()
            ).decode(),
            created_at=datetime.utcnow(),
        )

        teachers.append(teacher)

    db.bulk_save_objects(teachers)
    db.commit()

    print(f"✅ Inserted {NUM_TEACHERS} teachers")

finally:
    db.close()