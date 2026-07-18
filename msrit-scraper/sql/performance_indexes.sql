-- performance_indexes.sql

CREATE INDEX IF NOT EXISTS idx_attendance_student_scraped
ON attendance_records(student_id, scraped_at DESC);

CREATE INDEX IF NOT EXISTS idx_attendance_percentage
ON attendance_records(attendance_percentage);

CREATE INDEX IF NOT EXISTS idx_students_teacher
ON students(teacher_id);

CREATE INDEX IF NOT EXISTS idx_students_semester
ON students(semester);

CREATE INDEX IF NOT EXISTS idx_teachers_email
ON teachers(email);