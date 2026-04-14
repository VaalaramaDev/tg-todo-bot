import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.database import queries
from bot.keyboards import stats_keyboard

logger = logging.getLogger(__name__)


def _progress_bar(done: int, total: int) -> str:
    """Return a 10-character progress bar string."""
    pct = round(done / total * 100)
    filled = round(pct / 10)
    return "█" * filled + "░" * (10 - filled)


def _motivational_line(pct: int) -> str:
    """Return a motivational message based on completion percentage."""
    if pct == 0:
        return "Let's get started! 💪"
    if pct < 50:
        return "Good start! Keep going."
    if pct < 80:
        return "More than halfway there! 🔥"
    if pct < 100:
        return "Almost done! 🎯"
    return "All done! You're on fire! 🏆"


def build_stats_text(user_id: int) -> str:
    """Build the formatted stats string for a user."""
    stats = queries.get_stats(user_id)
    total = stats["total"]
    done = stats["done"]
    pending = stats["pending"]

    if total == 0:
        return "📊 Your statistics\n\nNo tasks yet. Use /add to get started."

    pct = round(done / total * 100)
    bar = _progress_bar(done, total)
    motivation = _motivational_line(pct)

    return (
        f"📊 Your statistics\n\n"
        f"✅ Completed    {done}\n"
        f"⏳ Pending      {pending}\n"
        f"📝 Total       {total}\n\n"
        f"Progress  {bar}  {pct}%\n\n"
        f"{motivation}"
    )


async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /stats command — display task statistics for the user."""
    user_id = update.effective_user.id
    await update.message.reply_text(
        build_stats_text(user_id),
        reply_markup=stats_keyboard(),
    )
