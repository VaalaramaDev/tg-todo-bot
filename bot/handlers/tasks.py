import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.database import queries

logger = logging.getLogger(__name__)


async def add_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /add <text> — create a new task for the user."""
    user_id = update.effective_user.id

    if not context.args:
        await update.message.reply_text(
            "⚠️ Usage: /add <task text>\nExample: /add Buy groceries"
        )
        return

    text = " ".join(context.args)
    task_id = queries.add_task(user_id, text)

    # Determine the 1-based display index of the newly added task.
    tasks = queries.get_tasks(user_id)
    display_index = len(tasks)  # new task is always last

    await update.message.reply_text(
        f"✅ Task added!\n\n#{display_index} {text}"
    )


async def list_tasks(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /list — show all pending tasks for the user."""
    user_id = update.effective_user.id
    tasks = queries.get_tasks(user_id)

    if not tasks:
        await update.message.reply_text(
            "✅ You have no active tasks. Use /add to create one!"
        )
        return

    lines = ["📋 *Your tasks:*\n"]
    for index, task in enumerate(tasks, start=1):
        lines.append(f"{index}. {task['text']}")

    count = len(tasks)
    lines.append(f"\nTotal: {count} active task{'s' if count != 1 else ''}")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def done_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /done <id> — mark the task at display index <id> as completed."""
    user_id = update.effective_user.id

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "⚠️ Usage: /done <task number>\nExample: /done 2"
        )
        return

    display_index = int(context.args[0])
    task = queries.get_task_by_user_index(user_id, display_index)

    if task is None:
        await update.message.reply_text(
            f"❌ Task #{display_index} not found. Use /list to see your tasks."
        )
        return

    updated = queries.mark_done(task["id"], user_id)
    if updated:
        await update.message.reply_text(
            f'🎉 Task #{display_index} completed!\n\n"{task["text"]}"'
        )
    else:
        await update.message.reply_text(
            f"❌ Could not complete task #{display_index}. It may already be done."
        )


async def delete_task(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /delete <id> — permanently delete the task at display index <id>."""
    user_id = update.effective_user.id

    if not context.args or not context.args[0].isdigit():
        await update.message.reply_text(
            "⚠️ Usage: /delete <task number>\nExample: /delete 3"
        )
        return

    display_index = int(context.args[0])
    task = queries.get_task_by_user_index(user_id, display_index)

    if task is None:
        await update.message.reply_text(
            f"❌ Task #{display_index} not found. Use /list to see your tasks."
        )
        return

    deleted = queries.delete_task(task["id"], user_id)
    if deleted:
        await update.message.reply_text(
            f'🗑️ Task #{display_index} deleted.\n\n"{task["text"]}"'
        )
    else:
        await update.message.reply_text(
            f"❌ Could not delete task #{display_index}."
        )
