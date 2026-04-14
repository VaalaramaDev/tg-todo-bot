from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def main_menu_keyboard() -> InlineKeyboardMarkup:
    """Main menu shown after /start and as the 'home' button."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add task",   callback_data="menu_add"),
            InlineKeyboardButton("📋 My tasks",   callback_data="menu_list"),
        ],
        [
            InlineKeyboardButton("🔔 Reminders",  callback_data="menu_reminders"),
            InlineKeyboardButton("📊 Stats",      callback_data="menu_stats"),
        ],
        [
            InlineKeyboardButton("❓ Help",        callback_data="menu_help"),
        ],
    ])


def tasks_action_keyboard() -> InlineKeyboardMarkup:
    """Shown below the task list."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add",        callback_data="menu_add"),
            InlineKeyboardButton("✅ Mark done",  callback_data="action_done_prompt"),
            InlineKeyboardButton("🗑 Delete",     callback_data="action_delete_prompt"),
        ],
        [
            InlineKeyboardButton("🏠 Home",       callback_data="menu_home"),
        ],
    ])


def after_add_keyboard() -> InlineKeyboardMarkup:
    """Shown after successfully adding a task, and for an empty task list."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("➕ Add another", callback_data="menu_add"),
            InlineKeyboardButton("📋 My tasks",    callback_data="menu_list"),
        ],
        [InlineKeyboardButton("🏠 Home",           callback_data="menu_home")],
    ])


def after_done_keyboard() -> InlineKeyboardMarkup:
    """Shown after completing a task."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📋 Back to tasks", callback_data="menu_list"),
            InlineKeyboardButton("📊 My stats",      callback_data="menu_stats"),
        ],
        [InlineKeyboardButton("🏠 Home",             callback_data="menu_home")],
    ])


def after_delete_keyboard() -> InlineKeyboardMarkup:
    """Shown after deleting a task."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📋 My tasks",  callback_data="menu_list"),
            InlineKeyboardButton("➕ Add task",  callback_data="menu_add"),
        ],
        [InlineKeyboardButton("🏠 Home",         callback_data="menu_home")],
    ])


def reminders_keyboard() -> InlineKeyboardMarkup:
    """Shown below the reminders list."""
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("❌ Cancel reminder", callback_data="action_cancel_prompt"),
            InlineKeyboardButton("📋 Tasks",           callback_data="menu_list"),
        ],
        [InlineKeyboardButton("🏠 Home",               callback_data="menu_home")],
    ])


def stats_keyboard() -> InlineKeyboardMarkup:
    """Shown below the stats message."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Back to tasks", callback_data="menu_list")],
        [InlineKeyboardButton("🏠 Home",          callback_data="menu_home")],
    ])


def help_keyboard() -> InlineKeyboardMarkup:
    """Shown below the help message."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Go to tasks",  callback_data="menu_list")],
        [InlineKeyboardButton("🏠 Home",         callback_data="menu_home")],
    ])


def back_home_keyboard() -> InlineKeyboardMarkup:
    """Minimal keyboard for error/info messages."""
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🏠 Home", callback_data="menu_home")],
    ])
