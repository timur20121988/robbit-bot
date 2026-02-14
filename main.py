import asyncio
import logging
import os
from aiohttp import web
from aiogram import Bot, Dispatcher
from config import BOT_TOKEN
from handlers import admin, user
from utils.db_api import init_db, get_all_chats, get_homework
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from datetime import datetime, timedelta

# Logging setup
logging.basicConfig(level=logging.INFO)

async def daily_reminder(bot: Bot):
    """Check for tomorrow's HW and send reminder"""
    tomorrow = datetime.now().date() + timedelta(days=1)
    # We just check if there are subjects
    from utils.db_api import get_homework_subjects
    subjects = await get_homework_subjects(tomorrow)
    
    if not subjects:
        return # No HW tomorrow, no alarm
        
    chats = await get_all_chats()
    msg_text = f"🔔 **Напоминание!**\nНе забудьте сделать ДЗ на завтра ({tomorrow.strftime('%d.%m.%Y')}).\nВведите /dz завтра, чтобы посмотреть."
    
    for chat_id in chats:
        try:
            await bot.send_message(chat_id, msg_text, parse_mode="Markdown")
        except Exception:
            pass

# --- Keep-alive web server for Render ---
async def handle(request):
    return web.Response(text="Bot is running!")

async def run_web_server():
    app = web.Application()
    app.router.add_get("/", handle)
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    print(f"Web server started on port {port}")

async def main():
    # Initialize DB
    await init_db()

    # Start web server (for Render keep-alive)
    await run_web_server()
    
    # Initialize Bot and Dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Register routers
    dp.include_router(admin.router)
    dp.include_router(user.router)
    
    # Setup Scheduler
    scheduler = AsyncIOScheduler()
    # Schedule reminder every day at 15:00 (can be changed)
    scheduler.add_job(daily_reminder, 'cron', hour=15, minute=0, args=[bot])
    scheduler.start()
    
    # Set Bot Description and Commands
    await bot.set_my_description(
        "📅 Школьный бот-помощник.\n\n"
        "✅ Домашнее задание на 10 дней вперед\n"
        "✅ Расписание уроков\n"
        "✅ Уведомления о новых заданиях\n\n"
        "Нажми /start, чтобы начать пользоваться!"
    )
    await bot.set_my_short_description("ДЗ, Расписание, Уведомления")
    
    from aiogram.types import BotCommand
    commands = [
        BotCommand(command="start", description="Запустить бота"),
        BotCommand(command="dzd", description="Найти ДЗ (10 дней)"),
        BotCommand(command="raspisanie", description="Расписание"),
        BotCommand(command="help", description="Помощь"),
        BotCommand(command="cancel", description="Отмена действия")
    ]
    await bot.set_my_commands(commands)
    
    # Start polling
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot stopped")
