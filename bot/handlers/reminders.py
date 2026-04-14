import logging
import re
from telegram import Update
from telegram.ext import ContextTypes
from bot.database import queries
from bot.scheduler import schedule_reminder, remove_reminder_job
from bot.keyboards import reminders_keyboard, back_home_keyboard

logger = logging.getLogger(__name__)

_TIME_RE = re.compile(r"^([01]\d|2[0-3]):([0-5]\d)$")


def build_reminders_text(user_id: int) -> str:
    """
    Build the formatted reminders list string for a user.

    Returns an empty string if the user has no active reminders.
    """
    reminders = queries.get_reminders(user_id)
    if not reminders:
        return ""

    count = len(reminders)
    lines = [f"🔔 Your reminders   {count} active\n"]
    for reminder in reminders:
        lines.append(
            f" Task #{reminder['task_id']}  \"{reminder['task_text']}\"      {reminder['remind_time']} UTC"
        )
    lines.append("\nAll times are UTC · fires daily.")
    lines.append("To cancel: /cancel <task number>")
    return "\n".join(lines)


async def remind_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /remind <id> <HH:MM> — set a daily reminder for a task."""
    user_id = update.effective_user.id

    if len(context.args) != 2:
        await update.message.reply_text(
            "⚠️ Usage: /remind <task number> <HH:MM>\nExample: /remind 1 09:00",
            reply_markup=back_home_keyboard(),
        )
        return

    id_arg, time_arg = context.args
    if not id_arg.isdigit():
        await update.message.reply_text(
            "⚠️ Usage: /remind <task number> <HH:MM>\nExample: /remind 1 09:00",
            reply_markup=back_home_keyboard(),
        )
        return

    if not _TIME_RE.match(time_arg):
        await update.message.reply_text(
            "⚠️ Invalid time format. Use HH:MM (24-hour UTC).\nExample: /remind 1 09:00",
            reply_markup=back_home_keyboard(),
        )
        return

    display_index = int(id_arg)
    task = queries.get_task_by_user_index(user_id, display_index)

    if task is None:
        await update.message.reply_text(
            f"❌ Task #{display_index} not found. Use /list to see your tasks.",
            reply_markup=back_home_keyboard(),
        )
        return

    hour, minute = map(int, time_arg.split(":"))

    queries.add_reminder(user_id, task["id"], time_arg)

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
        f'⏰ Reminder set!\n\nTask: "{task["text"]}"\nEvery day at {time_arg} UTC',
        reply_markup=reminders_keyboard(),
    )


async def list_reminders(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /reminders — list all active reminders for the user."""
    user_id = update.effective_user.id
    text = build_reminders_text(user_id)

    if not text:
        await update.message.reply_text(
            "You have no active reminders.\n\nTo set one: /remind <task number> <HH:MM>\nExample: /remind 1 09:00",
            reply_markup=back_home_keyboard(),
        )
        return

    await update.message.reply_text(text, reply_markup=reminders_keyboard())


async def cancel_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /cancel <id> — cancel the reminder for the task at display index <id>."""
    user_id = update.effective_user.id

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "⚠️ Usage: /cancel <task number>\nExample: /cancel 1",
            reply_markup=back_home_keyboard(),
        )
        return

    display_index = int(context.args[0])
    task = queries.get_task_by_user_index(user_id, display_index)

    if task is None:
        await update.message.reply_text(
            f"❌ Task #{display_index} not found. Use /list to see your tasks.",
            reply_markup=back_home_keyboard(),
        )
        return

    deactivated = queries.deactivate_reminder(task["id"], user_id)

    if deactivated:
        scheduler = context.bot_data["scheduler"]
        remove_reminder_job(scheduler, user_id, task["id"])
        await update.message.reply_text(
            f'🔕 Reminder cancelled.\n\n"{task["text"]}" — no longer reminded.',
            reply_markup=reminders_keyboard(),
        )
    else:
        await update.message.reply_text(
            f"❌ No active reminder found for task #{display_index}.",
            reply_markup=back_home_keyboard(),
        )
