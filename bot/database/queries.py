import sqlite3
import logging
from typing import Optional
from bot.database.connection import get_connection

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Task queries
# ---------------------------------------------------------------------------

def add_task(user_id: int, text: str) -> int:
    """Insert a new pending task and return its database id."""
    with get_connection() as conn:
        cursor = conn.execute(
            "INSERT INTO tasks (user_id, text) VALUES (?, ?)",
            (user_id, text),
        )
        return cursor.lastrowid


def get_tasks(user_id: int) -> list[sqlite3.Row]:
    """Return all pending tasks for a user, ordered by creation time."""
    with get_connection() as conn:
        rows = conn.execute(
            "SELECT * FROM tasks WHERE user_id = ? AND status = 'pending' ORDER BY created_at",
            (user_id,),
        ).fetchall()
    return rows


def get_task_by_user_index(user_id: int, index: int) -> Optional[sqlite3.Row]:
    """
    Return the task at the given 1-based display index for the user.

    The display index is the position of the task in the user's pending task
    list (ordered by created_at). Returns None if no match found.
    """
    tasks = get_tasks(user_id)
    if index < 1 or index > len(tasks):
        return None
    return tasks[index - 1]


def get_task_by_id(task_id: int, user_id: int) -> Optional[sqlite3.Row]:
    """Return a task by its real database id, scoped to the user."""
    with get_connection() as conn:
        row = conn.execute(
            "SELECT * FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id),
        ).fetchone()
    return row


def mark_done(task_id: int, user_id: int) -> bool:
    """Mark a task as done. Returns True if a row was updated."""
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE tasks SET status = 'done', done_at = datetime('now') "
            "WHERE id = ? AND user_id = ? AND status = 'pending'",
            (task_id, user_id),
        )
        return cursor.rowcount > 0


def delete_task(task_id: int, user_id: int) -> bool:
    """Permanently delete a task. Returns True if a row was deleted."""
    with get_connection() as conn:
        cursor = conn.execute(
            "DELETE FROM tasks WHERE id = ? AND user_id = ?",
            (task_id, user_id),
        )
        return cursor.rowcount > 0


def get_stats(user_id: int) -> dict:
    """Return task statistics for the user as {total, done, pending}."""
    with get_connection() as conn:
        row = conn.execute(
            """
            SELECT
                COUNT(*)                                        AS total,
                SUM(CASE WHEN status = 'done'    THEN 1 ELSE 0 END) AS done,
                SUM(CASE WHEN status = 'pending' THEN 1 ELSE 0 END) AS pending
            FROM tasks
            WHERE user_id = ?
            """,
            (user_id,),
        ).fetchone()
    return {
        "total":   row["total"]   or 0,
        "done":    row["done"]    or 0,
        "pending": row["pending"] or 0,
    }


# ---------------------------------------------------------------------------
# Reminder queries
# ---------------------------------------------------------------------------

def add_reminder(user_id: int, task_id: int, remind_time: str) -> int:
    """
    Insert an active reminder and return its id.

    If an active reminder already exists for this task, deactivate it first
    so there is never more than one active reminder per task.
    """
    with get_connection() as conn:
        conn.execute(
            "UPDATE reminders SET is_active = 0 WHERE task_id = ? AND user_id = ? AND is_active = 1",
            (task_id, user_id),
        )
        cursor = conn.execute(
            "INSERT INTO reminders (user_id, task_id, remind_time) VALUES (?, ?, ?)",
            (user_id, task_id, remind_time),
        )
        return cursor.lastrowid


def get_reminders(user_id: int) -> list[sqlite3.Row]:
    """Return all active reminders for a user, including the task text."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT r.id, r.task_id, r.remind_time, t.text AS task_text
            FROM reminders r
            JOIN tasks t ON t.id = r.task_id
            WHERE r.user_id = ? AND r.is_active = 1
            ORDER BY r.remind_time
            """,
            (user_id,),
        ).fetchall()
    return rows


def deactivate_reminder(task_id: int, user_id: int) -> bool:
    """Deactivate all active reminders for a task. Returns True if any updated."""
    with get_connection() as conn:
        cursor = conn.execute(
            "UPDATE reminders SET is_active = 0 WHERE task_id = ? AND user_id = ? AND is_active = 1",
            (task_id, user_id),
        )
        return cursor.rowcount > 0


def get_all_active_reminders() -> list[sqlite3.Row]:
    """Return all active reminders across all users (used on bot restart)."""
    with get_connection() as conn:
        rows = conn.execute(
            """
            SELECT r.id, r.user_id, r.task_id, r.remind_time, t.text AS task_text
            FROM reminders r
            JOIN tasks t ON t.id = r.task_id
            WHERE r.is_active = 1
            ORDER BY r.user_id, r.remind_time
            """,
        ).fetchall()
    return rows
