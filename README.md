# 🤖 Telegram To-Do Bot

A personal task manager bot for Telegram with daily reminders, inline keyboard UI, and per-user data isolation. Built as a portfolio project demonstrating Telegram Bot API, SQLite, APScheduler, and Docker deployment.

![Python](https://img.shields.io/badge/Python-3.11+-blue)
![python-telegram-bot](https://img.shields.io/badge/python--telegram--bot-20.7-blue)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED)
![License](https://img.shields.io/badge/license-MIT-green)

---

## Features

- Add, view, complete, and delete tasks
- Daily reminders at a custom time (UTC)
- Inline keyboard buttons — no need to remember commands
- Visual task list with reminder badges
- Completion progress bar in stats
- Full per-user data isolation — each user sees only their own tasks
- Reminders survive bot restarts (persisted in SQLite, restored on startup)

---

## Bot Commands

| Command               | Description                       |
| --------------------- | --------------------------------- |
| `/start`              | Open main menu                    |
| `/add <text>`         | Add a new task                    |
| `/list`               | Show active tasks                 |
| `/done <n>`           | Mark task #n as completed         |
| `/delete <n>`         | Delete task #n                    |
| `/remind <n> <HH:MM>` | Set a daily reminder at HH:MM UTC |
| `/reminders`          | List all active reminders         |
| `/cancel <n>`         | Cancel reminder for task #n       |
| `/stats`              | View completion statistics        |
| `/help`               | Full help                         |

---

## Tech Stack

| Layer         | Technology                       |
| ------------- | -------------------------------- |
| Language      | Python 3.11+                     |
| Bot framework | python-telegram-bot 20.7 (async) |
| Database      | SQLite via built-in `sqlite3`    |
| Scheduler     | APScheduler 3.10.4               |
| Config        | python-dotenv                    |
| Deployment    | Docker + Docker Compose          |

---

## Project Structure

```
tg-todo-bot/
├── bot/
│   ├── handlers/
│   │   ├── start.py        # /start, /help
│   │   ├── tasks.py        # /add, /list, /done, /delete
│   │   ├── reminders.py    # /remind, /reminders, /cancel
│   │   ├── stats.py        # /stats
│   │   └── callbacks.py    # inline keyboard button router
│   ├── database/
│   │   ├── connection.py   # DB init
│   │   └── queries.py      # all SQL queries
│   ├── keyboards.py        # all InlineKeyboardMarkup definitions
│   └── scheduler.py        # reminder jobs + restore on startup
├── main.py                 # entry point
├── config.py               # env vars
├── requirements.txt
├── .env.example
├── Dockerfile
└── docker-compose.yml
```

---

## Quick Start (Local)

### 1. Clone the repository

```bash
git clone https://github.com/VaalaramaDev/tg-todo-bot.git
cd tg-todo-bot
```

### 2. Create a bot via BotFather

1. Open [@BotFather](https://t.me/BotFather) in Telegram
2. Send `/newbot` and follow the prompts
3. Copy the bot token

### 3. Configure environment

```bash
cp .env.example .env
nano .env   # or open in any editor
```

Fill in your values:

```env
BOT_TOKEN=your_token_here
TIMEZONE=UTC
DB_PATH=data/todo.db
LOG_LEVEL=INFO
```

### 4. Run locally

```bash
# Create virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create data directory
mkdir -p data

# Start the bot
python main.py
```

### 5. Run with Docker

```bash
docker compose up -d --build
docker compose logs -f
```

---

## Deployment on VPS

This section covers deploying the bot on a Linux VPS (tested on Ubuntu 24.04, Hetzner CX43).

### Prerequisites

- VPS with Ubuntu 22.04 or 24.04
- SSH access
- Domain name (optional)

---

### Step 1 — Connect to your server

```bash
ssh root@YOUR_SERVER_IP
```

---

### Step 2 — Update the system

```bash
apt update && apt upgrade -y
```

---

### Step 3 — Install Docker

```bash
curl -fsSL https://get.docker.com | sh
```

Verify installation:

```bash
docker --version
docker compose version
```

---

### Step 4 — Clone the repository

```bash
mkdir -p ~/projects
cd ~/projects
git clone https://github.com/VaalaramaDev/tg-todo-bot.git
cd tg-todo-bot
```

---

### Step 5 — Create .env on the server

```bash
cp .env.example .env
nano .env
```

Add your bot token and save (`Ctrl+O` → `Enter` → `Ctrl+X`):

```env
BOT_TOKEN=your_token_here
TIMEZONE=Europe/Moscow
DB_PATH=data/todo.db
LOG_LEVEL=INFO
```

> ⚠️ Never commit `.env` to git. It is listed in `.gitignore`.

---

### Step 6 — Start the bot

```bash
docker compose up -d --build
```

Check it's running:

```bash
docker compose ps
docker compose logs -f
```

You should see:

```
Bot is starting...
Application started
```

Open Telegram, find your bot, send `/start`. If it responds — deployment is complete.

---

### Updating the bot after code changes

```bash
# On your local machine:
git add .
git commit -m "feat: your change"
git push

# On the VPS:
cd ~/projects/tg-todo-bot
git pull
docker compose up -d --build
```

---

### Useful management commands

```bash
# View live logs
docker compose logs -f

# View last 100 lines
docker compose logs --tail=100

# Stop the bot
docker compose stop

# Start the bot
docker compose start

# Full rebuild (after Dockerfile or requirements.txt changes)
docker compose up -d --build

# Open a shell inside the container
docker compose exec bot bash

# Inspect the database
docker compose exec bot sqlite3 data/todo.db ".tables"
docker compose exec bot sqlite3 data/todo.db "SELECT * FROM tasks;"
```

---

## Environment Variables

| Variable    | Default        | Description                                     |
| ----------- | -------------- | ----------------------------------------------- |
| `BOT_TOKEN` | required       | Token from [@BotFather](https://t.me/BotFather) |
| `TIMEZONE`  | `UTC`          | Timezone for reminders (e.g. `Europe/Moscow`)   |
| `DB_PATH`   | `data/todo.db` | Path to SQLite database file                    |
| `LOG_LEVEL` | `INFO`         | Logging level (`DEBUG`, `INFO`, `WARNING`)      |

---

## Database Schema

### tasks

| Column       | Type    | Description                |
| ------------ | ------- | -------------------------- |
| `id`         | INTEGER | Primary key                |
| `user_id`    | INTEGER | Telegram user ID           |
| `text`       | TEXT    | Task description           |
| `status`     | TEXT    | `pending` or `done`        |
| `created_at` | TEXT    | Creation timestamp (UTC)   |
| `done_at`    | TEXT    | Completion timestamp (UTC) |

### reminders

| Column        | Type    | Description               |
| ------------- | ------- | ------------------------- |
| `id`          | INTEGER | Primary key               |
| `user_id`     | INTEGER | Telegram user ID          |
| `task_id`     | INTEGER | FK → tasks.id             |
| `remind_time` | TEXT    | Daily time `HH:MM` (UTC)  |
| `is_active`   | INTEGER | `1` active, `0` cancelled |

---

## Security Notes

- Bot token is never logged (httpx logging set to WARNING)
- `.env` is gitignored — never appears in repository
- Each user accesses only their own data (all queries filter by `user_id`)
- Database file stored in Docker volume — persists across container restarts and rebuilds

---

## License

MIT — free to use, modify, and distribute.
