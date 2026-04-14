import logging
from datetime import datetime, timezone
from telegram import Update
from telegram.ext import ContextTypes
from bot.database import queries
from bot.keyboards import (
    tasks_action_keyboard,
    after_add_keyboard,
    after_done_keyboard,
    after_delete_keyboard,
    back_home_keyboard,
)

logger = logging.getLogger(__name__)


def build_task_list_text(user_id: int) -> str:
    """
    Build the formatted task list string for a user.

    Returns a ready-to-send string. Includes 🔔 HH:MM badge for tasks
    that have an active reminder. Returns an empty string if no tasks.
    """
    tasks = queries.get_tasks(user_id)
    if not tasks:
        return ""

    # Build a map of task_id → remind_time for quick lookup.
    reminders = queries.get_reminders(user_id)
    reminder_map = {row["task_id"]: row["remind_time"] for row in reminders}

    count = len(tasks)
    lines = [f"📋 Your tasks   {count} active\n"]
    for index, task in enumerate(tasks, start=1):
        reminder_badge = ""
        if task["id"] in reminder_map:
            reminder_badge = f"   🔔 {reminder_map[task['id']]}"
        lines.append(f" {index} ○  {task['text']}{reminder_badge}")

    lines.append("\nUse ✅ Mark done or 🗑 Delete to manage tasks.")
    lines.append("To set a reminder: /remind <n> HH:MM")
    return "\n".join(lines)


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /add <text> — create a new task for the user."""
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "⚠️ Usage: /add <task text>\nExample: /add Buy groceries",
            reply_markup=back_home_keyboard(),
        )
        return

    text = " ".join(context.args)
    queries.add_task(user_id, text)

    tasks = queries.get_tasks(user_id)
    display_index = len(tasks)
    count = len(tasks)

    await update.message.reply_text(
        f"✅ Task added!\n\n#{display_index}  {text}\n\nYou now have {count} active task{'s' if count != 1 else ''}.",
        reply_markup=after_add_keyboard(),
    )


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /list — show all pending tasks for the user."""
    user_id = update.effective_user.id
    text = build_task_list_text(user_id)

    if not text:
        await update.message.reply_text(
            "✅ You have no active tasks!\n\nTap ➕ Add task to create your first one.",
            reply_markup=after_add_keyboard(),
        )
        return

    await update.message.reply_text(text, reply_markup=tasks_action_keyboard())


async def done_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /done <id> — mark the task at display index <id> as completed."""
    user_id = update.effective_user.id

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "⚠️ Usage: /done <task number>\nExample: /done 2",
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

    updated = queries.mark_done(task["id"], user_id)
    if not updated:
        await update.message.reply_text(
            f"❌ Could not complete task #{display_index}. It may already be done.",
            reply_markup=back_home_keyboard(),
        )
        return

    now_utc = datetime.now(timezone.utc)
    timestamp = now_utc.strftime("%b %d · %H:%M UTC")
    remaining = len(queries.get_tasks(user_id))
    remaining_text = (
        f"{remaining} task{'s' if remaining != 1 else ''} remaining."
        if remaining > 0
        else "No tasks left — you're all caught up! 🏆"
    )

    await update.message.reply_text(
        f'🎉 Done!\n\n"{task["text"]}" — completed ✓\n{timestamp}\n\n{remaining_text}',
        reply_markup=after_done_keyboard(),
    )


async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /delete <id> — permanently delete the task at display index <id>."""
    user_id = update.effective_user.id

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "⚠️ Usage: /delete <task number>\nExample: /delete 3",
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

    deleted = queries.delete_task(task["id"], user_id)
    if deleted:
        await update.message.reply_text(
            f'🗑 Deleted.\n\n"{task["text"]}" has been removed.',
            reply_markup=after_delete_keyboard(),
        )
    else:
        await update.message.reply_text(
            f"❌ Could not delete task #{display_index}.",
            reply_markup=back_home_keyboard(),
        )
