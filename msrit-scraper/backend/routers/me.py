import logging
from typing import Optional

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.auth import get_current_teacher
from backend.schemas import LowAttendanceStudentOut, StudentOut
from backend import crud
from backend.routers.alerts import AlertSendRequest, AlertSendResponse, _build_notify_payload
from backend.notify_client import send_alert_to_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/me", tags=["Me"])


@router.get("/students", response_model=list[StudentOut], summary="Get my students")
def get_my_students(
    semester: Optional[str] = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(200, ge=1, le=500),
    db: Session = Depends(get_db),
    current_teacher=Depends(get_current_teacher),
):
    return crud.get_all_students(
        db, teacher_id=current_teacher.id, semester=semester, skip=skip, limit=limit
    )


@router.get(
    "/low-attendance",
    response_model=list[LowAttendanceStudentOut],
    summary="Get my low-attendance students",
)
def get_my_low_attendance(
    threshold: Optional[float] = Query(None, ge=0, le=100),
    db: Session = Depends(get_db),
    current_teacher=Depends(get_current_teacher),
):
    return crud.get_low_attendance_students(
        db, threshold=threshold, teacher_id=current_teacher.id
    )


def _fire_alert_background(payload: dict, teacher_id: int) -> None:
    """Runs in background — calls notification service without blocking the HTTP response."""
    try:
        result = send_alert_to_service(payload)
        logger.info(f"Background alert done for teacher id={teacher_id}: {result}")
    except RuntimeError as e:
        logger.error(f"Background alert failed for teacher id={teacher_id}: {e}")


@router.post(
    "/alerts/send",
    summary="Send attendance alerts for my students (fires in background)",
)
def send_my_alert(
    background_tasks: BackgroundTasks,
    body: AlertSendRequest = AlertSendRequest(),
    threshold: Optional[float] = Query(None, ge=0, le=100),
    db: Session = Depends(get_db),
    current_teacher=Depends(get_current_teacher),
):
    teacher = current_teacher

    if not teacher.email:
        raise HTTPException(
            status_code=422,
            detail=f"Teacher '{teacher.name}' has no email address in the database",
        )

    low_students = crud.get_low_attendance_students(
        db, threshold=threshold, teacher_id=teacher.id
    )

    if not low_students:
        logger.info(f"No low-attendance students for teacher id={teacher.id} — skipping")
        return JSONResponse(content={
            "teacher_id": teacher.id,
            "teacher_name": teacher.name,
            "teacher_email": teacher.email,
            "students_alerted": 0,
            "status": "skipped",
            "emails_sent": 0,
            "records_logged": 0,
            "detail": "No students below attendance threshold — no email sent",
        })

    payload = _build_notify_payload(
        teacher, low_students,
        notify_teacher=body.notify_teacher,
        notify_student=body.notify_student,
    )

    logger.info(
        f"Queuing background alert for teacher id={teacher.id}, {len(low_students)} student(s)"
    )

    # Calculate expected emails: 1 teacher summary + 1 per student (if enabled)
    expected_emails = (1 if body.notify_teacher else 0) + (len(low_students) if body.notify_student else 0)

    # Fire and return immediately — avoids Render's 30s connection timeout
    background_tasks.add_task(_fire_alert_background, payload, teacher.id)

    return JSONResponse(content={
        "teacher_id": teacher.id,
        "teacher_name": teacher.name,
        "teacher_email": teacher.email,
        "students_alerted": len(low_students),
        "status": "success",
        "emails_sent": expected_emails,
        "records_logged": 0,
        "detail": f"Alert queued for {len(low_students)} student(s) — emails sending in background",
    })
