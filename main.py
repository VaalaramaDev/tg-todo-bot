import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from telegram.ext import Application, CommandHandler

from config import BOT_TOKEN, TIMEZONE, LOG_LEVEL
from bot.database.connection import init_db
from bot.scheduler import load_reminders_from_db
from bot.handlers.start import start_handler, help_handler
from bot.handlers.tasks import add_task, list_tasks, done_task, delete_task
from bot.handlers.reminders import remind_handler, list_reminders, cancel_reminder
from bot.handlers.stats import stats_handler

logging.basicConfig(
    format="%(asctime)s | %(levelname)-8s | %(name)s — %(message)s",
    level=getattr(logging, LOG_LEVEL, logging.INFO),
)
logger = logging.getLogger(__name__)


async def post_init(application: Application) -> None:
    """Load reminders from the database after the bot has started."""
    scheduler: AsyncIOScheduler = application.bot_data["scheduler"]
    await load_reminders_from_db(application.bot, scheduler)


def main() -> None:
    """Entry point — initialise DB, start scheduler, register handlers, run bot."""
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN is not set. Check your .env file.")

    init_db()

    scheduler = AsyncIOScheduler(timezone=TIMEZONE)
    scheduler.start()

    app = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    app.bot_data["scheduler"] = scheduler

    app.add_handler(CommandHandler("start",     start_handler))
    app.add_handler(CommandHandler("help",      help_handler))
    app.add_handler(CommandHandler("add",       add_task))
    app.add_handler(CommandHandler("list",      list_tasks))
    app.add_handler(CommandHandler("done",      done_task))
    app.add_handler(CommandHandler("delete",    delete_task))
    app.add_handler(CommandHandler("remind",    remind_handler))
    app.add_handler(CommandHandler("reminders", list_reminders))
    app.add_handler(CommandHandler("cancel",    cancel_reminder))
    app.add_handler(CommandHandler("stats",     stats_handler))

    logger.info("Bot is starting...")
    app.run_polling()


if __name__ == "__main__":
    main()
