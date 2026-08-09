import logging
from datetime import datetime, timezone
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from sqlalchemy import select, cast, Date

from app.core.config import settings
from app.core.database import async_session
from app.models.sql_models import User, Expense
from app.core.email_service import send_expense_reminder_email

logger = logging.getLogger(__name__)

# Initialize the scheduler
scheduler = AsyncIOScheduler()

async def check_and_send_reminders():
    """
    Query all verified users who have not logged any expenses today,
    and send them a reminder email.
    """
    if not settings.REMINDER_ENABLED:
        logger.info("[SCHEDULER] Expense reminders are disabled via config.")
        return

    logger.info("[SCHEDULER] Running daily expense reminder check...")
    
    today = datetime.now(timezone.utc).date()

    async with async_session() as session:
        # Query users who do NOT have any expenses logged today
        stmt = select(User).where(
            User.is_verified == True,
            ~User.expenses.any(cast(Expense.date, Date) == today)
        )
        
        result = await session.execute(stmt)
        users_without_expenses = result.scalars().all()
        
        sent_count = 0
        for user in users_without_expenses:
            success = await send_expense_reminder_email(user.email, user.full_name)
            if success:
                sent_count += 1
                
    logger.info(f"[SCHEDULER] Finished sending reminders. Sent: {sent_count}, Total eligible: {len(users_without_expenses)}")

def setup_scheduler():
    """Configure scheduler jobs."""
    # Run every day at 21:00 (9 PM) server time
    scheduler.add_job(check_and_send_reminders, 'cron', hour=21, minute=0)
    logger.info("[SCHEDULER] Job configured to run daily at 21:00 server time.")
    
def start_scheduler():
    """Start the scheduler."""
    scheduler.start()
    logger.info("[SCHEDULER] Started.")

def stop_scheduler():
    """Stop the scheduler."""
    scheduler.shutdown()
    logger.info("[SCHEDULER] Shutdown.")
