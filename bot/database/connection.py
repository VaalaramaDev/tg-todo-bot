import sqlite3
import os
import logging
from config import DB_PATH

logger = logging.getLogger(__name__)


def get_connection() -> sqlite3.Connection:
    """Return a new SQLite connection with row_factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Initialize the database, creating tables if they do not exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with get_connection() as conn:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                text        TEXT    NOT NULL,
                status      TEXT    DEFAULT 'pending',
                created_at  TEXT    DEFAULT (datetime('now')),
                done_at     TEXT    DEFAULT NULL
            );

            CREATE TABLE IF NOT EXISTS reminders (
                id          INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id     INTEGER NOT NULL,
                task_id     INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                remind_time TEXT    NOT NULL,
                is_active   INTEGER DEFAULT 1,
                created_at  TEXT    DEFAULT (datetime('now'))
            );
        """)
    logger.info("Database initialised at %s", DB_PATH)
