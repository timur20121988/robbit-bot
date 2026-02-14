from aiogram import BaseMiddleware
from aiogram.types import Message
from config import ADMIN_IDS

class AdminMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            pass
        return await handler(event, data)

from aiogram.filters import Filter

class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        print(f"DEBUG: Check IsAdmin. User ID: {message.from_user.id} vs Admin IDs: {ADMIN_IDS}")
        return message.from_user.id in ADMIN_IDS

