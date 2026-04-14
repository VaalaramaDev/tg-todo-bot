import logging
import re
from telegram import Update
from telegram.ext import ContextTypes
from bot.database import queries
from bot.scheduler import schedule_reminder, remove_reminder_job

logger = logging.getLogger(__name__)

_TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


async def remind_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /remind <id> <HH:MM> — set a daily reminder for a task."""
    user_id = update.effective_user.id

    if len(context.args) != 2:
        await update.message.reply_text(
            "⚠️ Usage: /remind <task number> <HH:MM>\nExample: /remind 1 09:00"
        )
        return

    id_arg, time_arg = context.args
    if not id_arg.isdigit():
        await update.message.reply_text(
            "⚠️ Usage: /remind <task number> <HH:MM>\nExample: /remind 1 09:00"
        )
        return

    if not _TIME_RE.match(time_arg):
        await update.message.reply_text(
            "⚠️ Invalid time format. Use HH:MM (24-hour UTC).\nExample: /remind 1 09:00"
        )
        return

    display_index = int(id_arg)
    task = queries.get_task_by_user_index(user_id, display_index)

    if task is None:
        await update.message.reply_text(
            f"❌ Task #{display_index} not found. Use /list to see your tasks."
        )
        return

    hour, minute = map(int, time_arg.split(":"))

    # Persist to DB (replaces any existing active reminder for this task).
    queries.add_reminder(user_id, task["id"], time_arg)

    # Schedule in APScheduler.
    scheduler = context.bot_data["scheduler"]
    schedule_reminder(
        bot=context.bot,
        scheduler=scheduler,
        user_id=user_id,
        task_id=task["id"],
        task_text=task["text"],
        hour=hour,
        minute=minute,
    )

    await update.message.reply_text(
        f'⏰ Reminder set!\n\nTask: "{task["text"]}"\nEvery day at {time_arg} UTC'
    )


async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /reminders — list all active reminders for the user."""
    user_id = update.effective_user.id
    reminders = queries.get_reminders(user_id)

    if not reminders:
        await update.message.reply_text(
            "You have no active reminders. Use /remind <id> <HH:MM> to set one."
        )
        return

    lines = ["⏰ *Your reminders:*\n"]
    for reminder in reminders:
        lines.append(
            f"• Task #{reminder['task_id']}: \"{reminder['task_text']}\" — {reminder['remind_time']} UTC"
        )

    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def cancel_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cancel <id> — cancel the reminder for the task at display index <id>."""
    user_id = update.effective_user.id

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "⚠️ Usage: /cancel <task number>\nExample: /cancel 1"
        )
        return

    display_index = int(context.args[0])
    task = queries.get_task_by_user_index(user_id, display_index)

    if task is None:
        await update.message.reply_text(
            f"❌ Task #{display_index} not found. Use /list to see your tasks."
        )
        return

    deactivated = queries.deactivate_reminder(task["id"], user_id)

    if deactivated:
        scheduler = context.bot_data["scheduler"]
        remove_reminder_job(scheduler, user_id, task["id"])
        await update.message.reply_text(
            f'🔕 Reminder cancelled for task #{display_index}: "{task["text"]}"'
        )
    else:
        await update.message.reply_text(
            f"❌ No active reminder found for task #{display_index}."
        )
