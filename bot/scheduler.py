import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from telegram import Bot
from bot.database import queries

logger = logging.getLogger(__name__)


def _job_id(user_id: int, task_id: int) -> str:
    """Return a deterministic APScheduler job id for a user/task pair."""
    return f"reminder_{user_id}_{task_id}"


def schedule_reminder(
    bot: Bot,
    scheduler: AsyncIOScheduler,
    user_id: int,
    task_id: int,
    task_text: str,
    hour: int,
    minute: int,
) -> None:
    """
    Add or replace a daily cron job that sends a reminder message.

    If a job with the same id already exists it is replaced so that
    calling /remind twice updates the time correctly.
    """
    job_id = _job_id(user_id, task_id)

    async def send_reminder() -> None:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=f'⏰ Reminder: "{task_text}"',
            )
        except Exception as exc:
            logger.warning("Failed to send reminder %s: %s", job_id, exc)

    scheduler.add_job(
        send_reminder,
        trigger=CronTrigger(hour=hour, minute=minute, timezone="UTC"),
        id=job_id,
        replace_existing=True,
        name=f"reminder for user {user_id}, task {task_id}",
    )
    logger.info("Scheduled job %s at %02d:%02d UTC", job_id, hour, minute)


def remove_reminder_job(
    scheduler: AsyncIOScheduler, user_id: int, task_id: int
) -> None:
    """Remove the APScheduler job for a reminder if it exists."""
    job_id = _job_id(user_id, task_id)
    job = scheduler.get_job(job_id)
    if job:
        job.remove()
        logger.info("Removed job %s", job_id)


async def load_reminders_from_db(bot: Bot, scheduler: AsyncIOScheduler) -> None:
    """
    Re-schedule all active reminders from the database.

    Called once on bot startup so that reminders survive restarts.
    """
    reminders = queries.get_all_active_reminders()
    logger.info("Loading %d active reminder(s) from database", len(reminders))

    for reminder in reminders:
        try:
            hour, minute = map(int, reminder["remind_time"].split(":"))
            schedule_reminder(
                bot=bot,
                scheduler=scheduler,
                user_id=reminder["user_id"],
                task_id=reminder["task_id"],
                task_text=reminder["task_text"],
                hour=hour,
                minute=minute,
            )
        except Exception as exc:
            logger.error(
                "Could not restore reminder id=%d: %s", reminder["id"], exc
            )
