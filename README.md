# Telegram Homework Bot

Bot for managing school homework and schedules with an admin panel and reminders.

## Installation

1.  **Install Python** (if not installed).
2.  **Install dependencies**:
    ```bash
    pip install -r requirements.txt
    ```
3.  **Configuration**:
    - Rename `.env.example` to `.env`.
    - Open `.env` and set your `BOT_TOKEN` (from @BotFather) and `ADMIN_ID` (your Telegram user ID).
    - You can get your ID from bots like @userinfobot.

## Running the Bot

Run the following command:
```bash
python main.py
```

## Features

### Admin
- Type `/admin` to open the panel (only works for the ID specified in `.env`).
- **Add HW**: Follow the prompts to add homework with optional attachments.
- **Edit Schedule**: Set the text schedule for each day of the week.
- **Broadcast**: Send a message to all users/groups the bot is in.

### Users
- Add the bot to a group or use it privately.
- `/start` - Register the chat for notifications.
- `/dz` or **"ДЗ на сегодня"** - View today's homework.
- `/raspisanie` - View today's schedule.
- **Reminders**: Automatically sent at 15:00 if there is homework for tomorrow.

## Structure
- `data/` - Database file (auto-created).
- `handlers/` - Bot commands logic.
- `utils/db_api.py` - Database operations.
