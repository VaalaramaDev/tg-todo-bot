import logging
from telegram import Update
from telegram.ext import ContextTypes
from bot.keyboards import (
    main_menu_keyboard,
    after_add_keyboard,
    reminders_keyboard,
    back_home_keyboard,
    help_keyboard,
    stats_keyboard,
    tasks_action_keyboard,
)
from bot.handlers.start import WELCOME_TEXT, HELP_TEXT
from bot.handlers.tasks import build_task_list_text
from bot.handlers.reminders import build_reminders_text
from bot.handlers.stats import build_stats_text

logger = logging.getLogger(__name__)


async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Route all InlineKeyboard button presses to the appropriate handler."""
    query = update.callback_query
    await query.answer()  # removes the loading spinner on the button

    data = query.data
    user_id = query.from_user.id

    if data == "menu_home":
        await _show_home(query)
    elif data == "menu_list":
        await _show_list(query, user_id)
    elif data == "menu_add":
        await _prompt_add(query)
    elif data == "menu_reminders":
        await _show_reminders(query, user_id)
    elif data == "menu_stats":
        await _show_stats(query, user_id)
    elif data == "menu_help":
        await _show_help(query)
    elif data == "action_done_prompt":
        await _prompt_done(query)
    elif data == "action_delete_prompt":
        await _prompt_delete(query)
    elif data == "action_cancel_prompt":
        await _prompt_cancel(query)
    else:
        logger.warning("Unhandled callback_data: %r", data)


# ---------------------------------------------------------------------------
# View renderers — all use edit_message_text to update in-place
# ---------------------------------------------------------------------------

async def _show_home(query) -> None:
    await query.edit_message_text(WELCOME_TEXT, reply_markup=main_menu_keyboard())


async def _show_list(query, user_id: int) -> None:
    text = build_task_list_text(user_id)
    if not text:
        await query.edit_message_text(
            "✅ You have no active tasks!\n\nTap ➕ Add task to create your first one.",
            reply_markup=after_add_keyboard(),
        )
    else:
        await query.edit_message_text(text, reply_markup=tasks_action_keyboard())


async def _prompt_add(query) -> None:
    await query.edit_message_text(
        "➕ To add a task, type:\n/add <task text>\n\nExample: /add Buy groceries",
        reply_markup=back_home_keyboard(),
    )


async def _show_reminders(query, user_id: int) -> None:
    text = build_reminders_text(user_id)
    if not text:
        await query.edit_message_text(
            "You have no active reminders.\n\nTo set one: /remind <task number> <HH:MM>\nExample: /remind 1 09:00",
            reply_markup=back_home_keyboard(),
        )
    else:
        await query.edit_message_text(text, reply_markup=reminders_keyboard())


async def _show_stats(query, user_id: int) -> None:
    await query.edit_message_text(
        build_stats_text(user_id),
        reply_markup=stats_keyboard(),
    )


async def _show_help(query) -> None:
    await query.edit_message_text(
        HELP_TEXT,
        parse_mode="Markdown",
        reply_markup=help_keyboard(),
    )


async def _prompt_done(query) -> None:
    await query.edit_message_text(
        "✅ To mark a task done, type:\n/done <task number>\n\nExample: /done 2\nUse /list to see task numbers.",
        reply_markup=back_home_keyboard(),
    )


async def _prompt_delete(query) -> None:
    await query.edit_message_text(
        "🗑 To delete a task, type:\n/delete <task number>\n\nExample: /delete 2",
        reply_markup=back_home_keyboard(),
    )


async def _prompt_cancel(query) -> None:
    await query.edit_message_text(
        "🔕 To cancel a reminder, type:\n/cancel <task number>\n\nExample: /cancel 1\nUse /reminders to see active reminders.",
        reply_markup=back_home_keyboard(),
    )
