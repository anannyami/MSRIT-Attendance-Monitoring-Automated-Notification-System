from time import time

import requests
import time
from app.config import BREVO_API_KEY, ALERT_SENDER
from app.logger import get_logger
from app.schemas import NotifyRequest, StudentAlert

logger = get_logger(__name__)

BREVO_URL = "https://api.brevo.com/v3/smtp/email"


def _brevo_send(to_email: str, subject: str, html: str) -> tuple[bool, str]:
    # Simulate email provider latency
    time.sleep(0.2)
    return True, ""
"""
def _brevo_send(to_email: str, subject: str, html: str) -> tuple[bool, str]:
    #Send a single email via Brevo HTTP API.
    if not BREVO_API_KEY:
        return False, "BREVO_API_KEY not configured"
    if not ALERT_SENDER:
        return False, "ALERT_SENDER not configured"

    payload = {
        "sender":      {"name": "MSRIT Attendance", "email": ALERT_SENDER},
        "to":          [{"email": to_email}],
        "subject":     subject,
        "htmlContent": html,
    }
    try:
        resp = requests.post(
            BREVO_URL,
            json=payload,
            headers={"api-key": BREVO_API_KEY, "Content-Type": "application/json"},
            timeout=30,
        )
        if resp.status_code in (200, 201):
            return True, ""
        return False, f"Brevo API error {resp.status_code}: {resp.text}"
    except Exception as e:
        return False, f"Unexpected email error: {e}"
"""

# ── Teacher summary email ─────────────────────────────────────────────────────

def _build_teacher_html(req: NotifyRequest) -> str:
    total_subjects = sum(len(s.subjects) for s in req.students)
    rows = ""
    for student in req.students:
        first = True
        for subj in student.subjects:
            pct = subj.attendance_percentage
            color = "#e74c3c" if pct < 65 else "#e67e22" if pct < 75 else "#27ae60"
            if first:
                rows += f"""
                <tr>
                    <td rowspan="{len(student.subjects)}" style="padding:10px 12px;border:1px solid #ddd;vertical-align:top;font-weight:600;">{student.name}</td>
                    <td rowspan="{len(student.subjects)}" style="padding:10px 12px;border:1px solid #ddd;vertical-align:top;">{student.usn}</td>
                    <td rowspan="{len(student.subjects)}" style="padding:10px 12px;border:1px solid #ddd;vertical-align:top;">{student.semester}</td>
                    <td style="padding:10px 12px;border:1px solid #ddd;">{subj.subject_name}</td>
                    <td style="padding:10px 12px;border:1px solid #ddd;text-align:center;font-weight:700;color:{color};">{pct}%</td>
                    <td style="padding:10px 12px;border:1px solid #ddd;text-align:center;">{subj.attended_classes}/{subj.total_classes}</td>
                </tr>"""
                first = False
            else:
                rows += f"""
                <tr>
                    <td style="padding:10px 12px;border:1px solid #ddd;">{subj.subject_name}</td>
                    <td style="padding:10px 12px;border:1px solid #ddd;text-align:center;font-weight:700;color:{color};">{pct}%</td>
                    <td style="padding:10px 12px;border:1px solid #ddd;text-align:center;">{subj.attended_classes}/{subj.total_classes}</td>
                </tr>"""

    return f"""<!DOCTYPE html>
    <html>
    <body style="font-family:Arial,sans-serif;background:#f4f4f4;padding:24px;">
      <div style="max-width:750px;margin:auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
        <div style="background:#1a237e;padding:24px 32px;">
          <h2 style="color:#fff;margin:0;font-size:20px;">MSRIT — Attendance Alert</h2>
          <p style="color:#c5cae9;margin:6px 0 0;">Proctorship Notification System</p>
        </div>
        <div style="padding:28px 32px;">
          <p style="font-size:15px;color:#333;">Dear <strong>{req.teacher.name}</strong>,</p>
          <p style="font-size:14px;color:#555;line-height:1.6;">
            The following <strong>{len(req.students)} student(s)</strong> under your proctorship
            have <strong>{total_subjects} subject(s)</strong> with attendance below the required threshold.
            Please counsel them at the earliest.
          </p>
          <table style="width:100%;border-collapse:collapse;margin-top:16px;font-size:13px;">
            <thead>
              <tr style="background:#1a237e;color:#fff;">
                <th style="padding:10px 12px;text-align:left;border:1px solid #ddd;">Student Name</th>
                <th style="padding:10px 12px;text-align:left;border:1px solid #ddd;">USN</th>
                <th style="padding:10px 12px;text-align:left;border:1px solid #ddd;">Semester</th>
                <th style="padding:10px 12px;text-align:left;border:1px solid #ddd;">Subject</th>
                <th style="padding:10px 12px;text-align:center;border:1px solid #ddd;">Attendance %</th>
                <th style="padding:10px 12px;text-align:center;border:1px solid #ddd;">Attended/Total</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
          <p style="font-size:13px;color:#888;margin-top:24px;">
            This is an automated alert generated by the MSRIT Attendance Monitoring System.
            Please do not reply to this email.
          </p>
        </div>
        <div style="background:#f0f0f0;padding:14px 32px;text-align:center;">
          <p style="font-size:12px;color:#999;margin:0;">
            RAMAIAH INSTITUTE OF TECHNOLOGY &nbsp;|&nbsp; Department of Computer Science &amp; Engineering
          </p>
        </div>
      </div>
    </body>
    </html>"""


def send_email(req: NotifyRequest) -> tuple[bool, str]:
    """Send HTML summary alert to teacher via Brevo API."""
    subject = f"Attendance Alert — {len(req.students)} student(s) require attention"
    html    = _build_teacher_html(req)
    ok, err = _brevo_send(req.teacher.email, subject, html)
    if ok:
        logger.info(f"Teacher email sent to {req.teacher.email} via Brevo")
    else:
        logger.error(f"Teacher email failed: {err}")
    return ok, err


# ── Student personalized email ────────────────────────────────────────────────

def _build_student_html(student: StudentAlert, teacher_name: str) -> str:
    rows = ""
    for subj in student.subjects:
        pct = subj.attendance_percentage
        color = "#e74c3c" if pct < 65 else "#e67e22" if pct < 75 else "#27ae60"
        rows += f"""
        <tr>
            <td style="padding:10px 12px;border:1px solid #ddd;">{subj.subject_name}</td>
            <td style="padding:10px 12px;border:1px solid #ddd;text-align:center;font-weight:700;color:{color};">{pct}%</td>
            <td style="padding:10px 12px;border:1px solid #ddd;text-align:center;">{subj.attended_classes}/{subj.total_classes}</td>
        </tr>"""

    return f"""<!DOCTYPE html>
    <html>
    <body style="font-family:Arial,sans-serif;background:#f4f4f4;padding:24px;">
      <div style="max-width:650px;margin:auto;background:#fff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(0,0,0,0.1);">
        <div style="background:#1a237e;padding:24px 32px;">
          <h2 style="color:#fff;margin:0;font-size:20px;">MSRIT — Attendance Warning</h2>
          <p style="color:#c5cae9;margin:6px 0 0;">Student Attendance Notification</p>
        </div>
        <div style="padding:28px 32px;">
          <p style="font-size:15px;color:#333;">Dear <strong>{student.name}</strong>,</p>
          <p style="font-size:14px;color:#555;line-height:1.6;">
            Your attendance in the following subject(s) has fallen below the required threshold.
            Please meet your proctor <strong>{teacher_name}</strong> at the earliest.
          </p>
          <table style="width:100%;border-collapse:collapse;margin-top:16px;font-size:13px;">
            <thead>
              <tr style="background:#1a237e;color:#fff;">
                <th style="padding:10px 12px;text-align:left;border:1px solid #ddd;">Subject</th>
                <th style="padding:10px 12px;text-align:center;border:1px solid #ddd;">Attendance %</th>
                <th style="padding:10px 12px;text-align:center;border:1px solid #ddd;">Attended / Total</th>
              </tr>
            </thead>
            <tbody>{rows}</tbody>
          </table>
          <p style="font-size:13px;color:#555;margin-top:20px;">
            <strong>USN:</strong> {student.usn} &nbsp;|&nbsp; <strong>Semester:</strong> {student.semester}
          </p>
          <p style="font-size:13px;color:#888;margin-top:16px;">
            This is an automated alert. Please do not reply to this email.
          </p>
        </div>
        <div style="background:#f0f0f0;padding:14px 32px;text-align:center;">
          <p style="font-size:12px;color:#999;margin:0;">
            RAMAIAH INSTITUTE OF TECHNOLOGY &nbsp;|&nbsp; Department of Computer Science &amp; Engineering
          </p>
        </div>
      </div>
    </body>
    </html>"""


def send_student_email(student: StudentAlert, teacher_name: str) -> tuple[bool, str]:
    """Send personalized attendance warning to student via Brevo API."""
    if not student.student_email:
        reason = f"No email on record for student {student.usn} — skipped"
        logger.info(reason)
        return False, reason

    subject = f"Attendance Warning — {len(student.subjects)} subject(s) below threshold | {student.usn}"
    html    = _build_student_html(student, teacher_name)
    ok, err = _brevo_send(student.student_email, subject, html)
    if ok:
        logger.info(f"Student email sent to {student.student_email} ({student.usn}) via Brevo")
    else:
        logger.error(f"Student email failed for {student.usn}: {err}")
    return ok, err
