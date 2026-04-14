import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.database import queries

logger = logging.getLogger(__name__)


async def stats_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /stats command — display task statistics for the user."""
    user_id = update.effective_user.id
    stats = queries.get_stats(user_id)

    text = (
        "📊 *Your statistics:*\n\n"
        f"✅ Completed: {stats['done']}\n"
        f"⏳ Pending:   {stats['pending']}\n"
        f"📝 Total:     {stats['total']}"
    )
    await update.message.reply_text(text, parse_mode="Markdown")
