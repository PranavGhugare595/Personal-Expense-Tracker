from fastapi import APIRouter, Depends, HTTPException, status
from typing import Any

from app.api.deps import get_current_user
from app.core.email_service import send_reminder_email
from app.core.config import settings

router = APIRouter()


@router.post("/test-reminder", status_code=status.HTTP_200_OK)
def test_reminder_email(current_user: dict = Depends(get_current_user)) -> Any:
    """
    Immediately sends a test reminder email to the currently authenticated user.
    Useful for verifying your SMTP configuration without waiting for the 9 PM cron job.
    """
    if not settings.SMTP_EMAIL or not settings.SMTP_APP_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=(
                "Email service is not configured. "
                "Please set SMTP_EMAIL and SMTP_APP_PASSWORD in your backend/.env file."
            )
        )

    email = current_user.get("email", "")
    name = current_user.get("name", "Friend")

    success = send_reminder_email(to_email=email, user_name=name)

    if success:
        return {
            "status": "success",
            "message": f"✅ Reminder email sent successfully to {email}",
            "recipient": email
        }
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to send email to {email}. Check your SMTP credentials in .env."
        )


@router.post("/run-check", status_code=status.HTTP_200_OK)
def run_full_reminder_check(current_user: dict = Depends(get_current_user)) -> Any:
    """
    Manually triggers the full daily reminder job across ALL users.
    Returns a detailed report of who was reminded and who was skipped.
    Only call this for testing — normally the scheduler runs this automatically at 9 PM.
    """
    from app.core.scheduler import trigger_reminder_now

    results = trigger_reminder_now()
    reminded = [r for r in results if r["status"] == "sent"]
    skipped = [r for r in results if r["status"] == "skipped"]
    failed = [r for r in results if r["status"] == "failed"]

    return {
        "status": "completed",
        "summary": {
            "total_users": len(results),
            "reminded": len(reminded),
            "skipped_already_logged": len(skipped),
            "failed": len(failed),
        },
        "details": results,
        "note": "Normally this job fires automatically every day at 9 PM IST."
    }
