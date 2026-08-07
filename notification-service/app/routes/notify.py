from typing import Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import AlertLog
from app.schemas import NotifyRequest, NotifyResponse, AlertLogOut
from app.email_service import send_email, send_student_email
from app.logger import get_logger

logger = get_logger(__name__)
router = APIRouter()

# Maximum number of concurrent student email workers
MAX_EMAIL_WORKERS = 8


@router.post(
    "/notify",
    response_model=NotifyResponse,
    summary="Send attendance alert emails to teacher and/or students",
)
def notify(req: NotifyRequest, db: Session = Depends(get_db)):
    if not req.students:
        raise HTTPException(
            status_code=400,
            detail="students list cannot be empty",
        )

    if not req.notify_teacher and not req.notify_student:
        raise HTTPException(
            status_code=400,
            detail="At least one of notify_teacher or notify_student must be true",
        )

    logger.info(
        f"Notify request — teacher: {req.teacher.email}, "
        f"students: {len(req.students)}, "
        f"notify_teacher={req.notify_teacher}, "
        f"notify_student={req.notify_student}"
    )

    emails_sent = 0
    log_entries: list[AlertLog] = []

    # ==========================================================
    # 1. Send Teacher Summary Email
    # ==========================================================

    teacher_ok = False
    teacher_err = ""

    if req.notify_teacher:
        teacher_ok, teacher_err = send_email(req)

        if teacher_ok:
            emails_sent += 1

        for student in req.students:
            for subj in student.subjects:
                log_entries.append(
                    AlertLog(
                        teacher_email=req.teacher.email,
                        student_name=student.name,
                        usn=student.usn,
                        subject_name=subj.subject_name,
                        attendance_percentage=subj.attendance_percentage,
                        status="success" if teacher_ok else "failed",
                        error_message=None if teacher_ok else teacher_err,
                        recipient_type="teacher",
                    )
                )

    # ==========================================================
    # 2. Send Student Emails Concurrently
    # ==========================================================

    if req.notify_student:

        students_with_email = [
            student
            for student in req.students
            if student.student_email
        ]

        if students_with_email:

            worker_count = min(
                MAX_EMAIL_WORKERS,
                len(students_with_email),
            )

            with ThreadPoolExecutor(max_workers=worker_count) as executor:

                future_to_student = {
                    executor.submit(
                        send_student_email,
                        student,
                        req.teacher.name,
                    ): student
                    for student in students_with_email
                }

                for future in as_completed(future_to_student):

                    student = future_to_student[future]

                    try:
                        student_ok, student_err = future.result()

                    except Exception as exc:
                        logger.exception(
                            f"Unexpected error while sending email to {student.usn}: {exc}"
                        )
                        student_ok = False
                        student_err = str(exc)

                    if student_ok:
                        emails_sent += 1

                    for subj in student.subjects:
                        log_entries.append(
                            AlertLog(
                                teacher_email=req.teacher.email,
                                student_name=student.name,
                                usn=student.usn,
                                subject_name=subj.subject_name,
                                attendance_percentage=subj.attendance_percentage,
                                status="success" if student_ok else "failed",
                                error_message=None if student_ok else student_err,
                                recipient_type="student",
                            )
                        )

        else:
            logger.info("No student email addresses available.")

       # ==========================================================
    # 3. Persist Log Entries
    # ==========================================================

    records_logged = 0

    try:
        db.add_all(log_entries)
        db.commit()

        records_logged = len(log_entries)

        logger.info(
            f"Logged {records_logged} alert records to database."
        )

    except Exception as e:
        logger.error(f"Database logging failed: {e}")
        db.rollback()

    # ==========================================================
    # 4. Build Response
    # ==========================================================

    any_sent = emails_sent > 0
    detail: Optional[str] = None

    if any_sent and records_logged > 0:
        status = "success"

    elif any_sent and records_logged == 0:
        status = "partial"
        detail = "Email(s) sent successfully but database logging failed."

    elif not any_sent and records_logged > 0:
        status = "partial"

        errors = []

        if req.notify_teacher and not teacher_ok:
            errors.append(f"Teacher email failed: {teacher_err}")

        if req.notify_student:
            errors.append("No student emails were sent.")

        detail = " | ".join(errors) if errors else "No emails sent."

    else:
        status = "failed"

        errors = []

        if req.notify_teacher and not teacher_ok:
            errors.append(f"Teacher email failed: {teacher_err}")

        if req.notify_student:
            errors.append("All student email attempts failed.")

        detail = "; ".join(errors) if errors else "All email attempts failed."

    return NotifyResponse(
        status=status,
        emails_sent=emails_sent,
        records_logged=records_logged,
        detail=detail,
    )


# ==========================================================
# Alert Log API
# ==========================================================

@router.get(
    "/alerts/logs",
    response_model=list[AlertLogOut],
    summary="Query alert log history",
)
def get_alert_logs(
    teacher_email: Optional[str] = Query(
        None,
        description="Filter by teacher email",
    ),
    usn: Optional[str] = Query(
        None,
        description="Filter by student USN",
    ),
    status: Optional[str] = Query(
        None,
        description="Filter by status",
    ),
    recipient_type: Optional[str] = Query(
        None,
        description="teacher | student",
    ),
    limit: int = Query(
        100,
        ge=1,
        le=1000,
    ),
    skip: int = Query(
        0,
        ge=0,
    ),
    db: Session = Depends(get_db),
):

    q = db.query(AlertLog)

    if teacher_email:
        q = q.filter(AlertLog.teacher_email == teacher_email)

    if usn:
        q = q.filter(AlertLog.usn == usn.upper())

    if status:
        q = q.filter(AlertLog.status == status)

    if recipient_type:
        q = q.filter(AlertLog.recipient_type == recipient_type)

    return (
        q.order_by(AlertLog.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )