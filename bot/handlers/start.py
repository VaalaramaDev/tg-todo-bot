import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import main_menu_keyboard, help_keyboard

logger = logging.getLogger(__name__)

WELCOME_TEXT = """\
👋 Welcome to To-Do Bot!

Your personal task manager with daily reminders.
Use the buttons below or type commands directly.\
"""

HELP_TEXT = """\
❓ *How To-Do Bot works*

📋 *Task Management*
  /add <text>    — Add a new task
  /list          — Show your active tasks
  /done <n>      — Mark task #n as done
  /delete <n>    — Delete task #n

⏰ *Reminders*
  /remind <n> <HH:MM>  — Daily reminder at HH:MM UTC
  /reminders            — See all reminders
  /cancel <n>           — Cancel reminder for task #n

📊 *Stats*
  /stats  — See your completion progress

💡 *Tips*
  • Task numbers shown in /list are what you use in all commands
  • Completed tasks are saved but not shown in /list
  • All reminder times are UTC
  • Tap 🏠 Home any time to return to the main menu\
"""


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /start command — send a welcome message with the main menu."""
    await update.message.reply_text(
        WELCOME_TEXT,
        reply_markup=main_menu_keyboard(),
    )


async def help_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command — send the full help text."""
    await update.message.reply_text(
        HELP_TEXT,
        parse_mode="Markdown",
        reply_markup=help_keyboard(),
    )
