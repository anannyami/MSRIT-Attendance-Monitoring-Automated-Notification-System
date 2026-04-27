import logging
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
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


@router.post(
    "/alerts/send",
    response_model=AlertSendResponse,
    summary="Send attendance alerts for my students",
)
def send_my_alert(
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
        return AlertSendResponse(
            teacher_id=teacher.id,
            teacher_name=teacher.name,
            teacher_email=teacher.email,
            students_alerted=0,
            status="skipped",
            emails_sent=0,
            records_logged=0,
            detail="No students below attendance threshold — no email sent",
        )

    payload = _build_notify_payload(
        teacher, low_students,
        notify_teacher=body.notify_teacher,
        notify_student=body.notify_student,
    )

    logger.info(
        f"Sending alert for teacher id={teacher.id}, {len(low_students)} student(s)"
    )

    try:
        result = send_alert_to_service(payload)
        return AlertSendResponse(
            teacher_id=teacher.id,
            teacher_name=teacher.name,
            teacher_email=teacher.email,
            students_alerted=len(low_students),
            status=result.get("status", "unknown"),
            emails_sent=result.get("emails_sent", 0),
            records_logged=result.get("records_logged", 0),
            detail=result.get("detail"),
        )
    except RuntimeError as e:
        logger.error(f"Notification service failed for teacher id={teacher.id}: {e}")
        return AlertSendResponse(
            teacher_id=teacher.id,
            teacher_name=teacher.name,
            teacher_email=teacher.email,
            students_alerted=len(low_students),
            status="failed",
            emails_sent=0,
            records_logged=0,
            detail=str(e),
        )
