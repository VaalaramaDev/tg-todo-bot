import logging
from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

WELCOME_MESSAGE = """\
👋 Welcome to your personal To-Do Bot!

I help you manage tasks and send daily reminders.

*Quick reference:*
/add <text>       — Add a new task
/list             — Show active tasks
/done <id>        — Mark task as completed
/delete <id>      — Delete a task
/remind <id> <HH:MM> — Set a daily reminder (UTC)
/reminders        — List your reminders
/cancel <id>      — Cancel a reminder
/stats            — View your statistics
/help             — Full help
"""

HELP_MESSAGE = """\
📖 *To-Do Bot — Help*

*Task Management*
/add <text>
  Add a new task. Example: `/add Buy groceries`

/list
  Show all your active (pending) tasks.

/done <id>
  Mark task #id as completed. Example: `/done 2`

/delete <id>
  Permanently delete task #id. Example: `/delete 3`

*Reminders*
/remind <id> <HH:MM>
  Set a daily reminder at HH:MM UTC for task #id.
  Example: `/remind 1 09:00`

/reminders
  List all your active reminders.

/cancel <id>
  Cancel the reminder for task #id. Example: `/cancel 1`

*Statistics*
/stats
  Show total, completed, and pending task counts.

*Notes*
• Task IDs are the numbers shown in /list.
• All reminder times are in UTC.
• Completed tasks are not shown in /list but counted in /stats.
"""


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command — send a welcome message."""
    await update.message.reply_text(WELCOME_MESSAGE, parse_mode="Markdown")


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command — send the full help text."""
    await update.message.reply_text(HELP_MESSAGE, parse_mode="Markdown")
