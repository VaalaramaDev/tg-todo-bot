# Telegram To-Do Bot

A personal task manager bot with daily reminders. Built with Python and python-telegram-bot.

## Features

- Add, view, complete, and delete tasks
- Daily reminders at a custom UTC time (persisted across restarts)
- Per-user data isolation — each user only sees their own tasks
- Task statistics (total / done / pending)
- Dockerised for easy deployment

## Stack

Python 3.11 · python-telegram-bot 20.7 · SQLite · APScheduler 3.10.4 · Docker

## Commands

| Command | Description |
|---|---|
| `/start` | Welcome message with quick command reference |
| `/help` | Full help with all commands and usage examples |
| `/add <text>` | Add a new task |
| `/list` | Show all active (pending) tasks |
| `/done <id>` | Mark task as completed |
| `/delete <id>` | Delete a task permanently |
| `/remind <id> <HH:MM>` | Set a daily reminder for a task (UTC) |
| `/reminders` | List all active reminders |
| `/cancel <id>` | Cancel a reminder by task number |
| `/stats` | Show statistics: total / done / pending |

## Quick Start

### Docker (recommended)

```bash
# 1. Clone the repo
git clone <repo-url>
cd tg-todo-bot

# 2. Create your .env file
cp .env.example .env
# Open .env and set BOT_TOKEN to your token from @BotFather

# 3. Start the bot
docker compose up -d --build
```

### Local

```bash
# 1. Create and activate a virtual environment
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your .env file
cp .env.example .env
# Open .env and set BOT_TOKEN

# 4. Create the data directory
mkdir -p data

# 5. Run the bot
python main.py
```

## Environment Variables

| Variable | Default | Description |
|---|---|---|
| `BOT_TOKEN` | required | Token from @BotFather |
| `TIMEZONE` | `UTC` | Scheduler timezone |
| `DB_PATH` | `data/todo.db` | SQLite file path |
| `LOG_LEVEL` | `INFO` | Logging level (`DEBUG`, `INFO`, `WARNING`, `ERROR`) |

## Project Structure

```
tg-todo-bot/
├── bot/
│   ├── handlers/
│   │   ├── start.py       # /start, /help
│   │   ├── tasks.py       # /add, /list, /done, /delete
│   │   ├── reminders.py   # /remind, /reminders, /cancel
│   │   └── stats.py       # /stats
│   ├── database/
│   │   ├── connection.py  # DB init & connection helper
│   │   └── queries.py     # All SQL query functions
│   └── scheduler.py       # APScheduler job management
├── main.py                # Entry point
├── config.py              # Environment config
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## Data Persistence

The SQLite database is stored in `./data/todo.db`. When running with Docker, this directory is mounted as a volume (`./data:/app/data`) so data survives container restarts. Active reminders are also restored from the database on every bot startup.
