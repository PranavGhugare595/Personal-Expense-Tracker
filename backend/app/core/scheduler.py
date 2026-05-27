import logging
from datetime import datetime, date
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.core.config import settings

logger = logging.getLogger("app.scheduler")

# Module-level scheduler instance
scheduler = BackgroundScheduler(timezone="Asia/Kolkata")


def _check_and_send_reminders():
    """
    Core job: scans every registered user and sends an email reminder
    if they have not logged a single expense today.
    """
    # Import inside function to avoid circular imports at module load time
    from app.core.database import db_manager
    from app.core.email_service import send_reminder_email

    today = date.today()
    today_str = today.isoformat()  # "2026-05-27"
    logger.info(f"[Scheduler] Running daily reminder job for date: {today_str}")

    try:
        all_users = db_manager.find_many("users", {})
    except Exception as e:
        logger.error(f"[Scheduler] Failed to fetch users: {e}")
        return

    total_users = len(all_users)
    reminded = 0
    skipped = 0

    for user in all_users:
        user_id = str(user.get("_id", ""))
        email = user.get("email", "")
        name = user.get("name", "Friend")

        if not email:
            continue

        # Check if user logged any expense today
        try:
            expenses_today = db_manager.find_many("expenses", {"userId": user_id})
        except Exception as e:
            logger.warning(f"[Scheduler] Could not query expenses for user {user_id}: {e}")
            continue

        # Filter to only today's expenses (date field may be ISO string or datetime)
        has_expense_today = False
        for exp in expenses_today:
            exp_date = exp.get("date", "")
            try:
                if isinstance(exp_date, datetime):
                    if exp_date.date() == today:
                        has_expense_today = True
                        break
                elif isinstance(exp_date, str):
                    # Handles "2026-05-27T..." or "2026-05-27"
                    if exp_date[:10] == today_str:
                        has_expense_today = True
                        break
            except Exception:
                continue

        if has_expense_today:
            logger.info(f"[Scheduler] {email} — has expenses today. No reminder needed.")
            skipped += 1
        else:
            logger.info(f"[Scheduler] {email} — no expenses today. Sending reminder...")
            success = send_reminder_email(to_email=email, user_name=name)
            if success:
                reminded += 1

    logger.info(
        f"[Scheduler] Job complete. Users: {total_users} | "
        f"Reminded: {reminded} | Skipped (already logged): {skipped}"
    )


def start_scheduler():
    """Starts the APScheduler background cron job."""
    if scheduler.running:
        logger.warning("[Scheduler] Scheduler is already running — skipping start.")
        return

    # Schedule: every day at REMINDER_HOUR:REMINDER_MINUTE (IST timezone)
    scheduler.add_job(
        func=_check_and_send_reminders,
        trigger=CronTrigger(
            hour=settings.REMINDER_HOUR,
            minute=settings.REMINDER_MINUTE,
            timezone="Asia/Kolkata"
        ),
        id="daily_expense_reminder",
        name="Daily Expense Reminder Email",
        replace_existing=True,
        misfire_grace_time=3600  # Allow up to 1 hour late execution
    )

    scheduler.start()
    logger.info(
        f"[Scheduler] Started. Reminders scheduled daily at "
        f"{settings.REMINDER_HOUR:02d}:{settings.REMINDER_MINUTE:02d} IST."
    )
    print(
        f"[INFO] Expense reminder scheduler started — "
        f"fires daily at {settings.REMINDER_HOUR:02d}:{settings.REMINDER_MINUTE:02d} IST."
    )


def stop_scheduler():
    """Gracefully shuts down the scheduler."""
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("[Scheduler] Scheduler shut down gracefully.")
        print("[INFO] Expense reminder scheduler stopped.")


def trigger_reminder_now():
    """
    Manually triggers the reminder job immediately (used by the test API endpoint).
    Returns a summary dict.
    """
    from app.core.database import db_manager
    from app.core.email_service import send_reminder_email

    today = date.today()
    today_str = today.isoformat()

    results = []
    all_users = db_manager.find_many("users", {})

    for user in all_users:
        user_id = str(user.get("_id", ""))
        email = user.get("email", "")
        name = user.get("name", "Friend")

        if not email:
            continue

        expenses_today = db_manager.find_many("expenses", {"userId": user_id})
        has_expense_today = False
        for exp in expenses_today:
            exp_date = exp.get("date", "")
            try:
                if isinstance(exp_date, datetime):
                    if exp_date.date() == today:
                        has_expense_today = True
                        break
                elif isinstance(exp_date, str):
                    if exp_date[:10] == today_str:
                        has_expense_today = True
                        break
            except Exception:
                continue

        if has_expense_today:
            results.append({"email": email, "status": "skipped", "reason": "Already logged expenses today"})
        else:
            success = send_reminder_email(to_email=email, user_name=name)
            results.append({
                "email": email,
                "status": "sent" if success else "failed",
                "reason": "No expenses logged today"
            })

    return results
