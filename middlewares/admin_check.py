from aiogram import BaseMiddleware
from aiogram.types import Message
from config import ADMIN_ID

class AdminMiddleware(BaseMiddleware):
    async def __call__(self, handler, event, data):
        if isinstance(event, Message):
            # We only restrict specific commands or handling flows if needed, 
            # but usually we use Filters for handlers. 
            # This class is just a placeholder if we wanted global restriction.
            pass
        return await handler(event, data)

# Actually, it's better to just use a Filter in the handler registration.
from aiogram.filters import Filter

class IsAdmin(Filter):
    async def __call__(self, message: Message) -> bool:
        print(f"DEBUG: Check IsAdmin. User ID: {message.from_user.id} vs Admin ID: {ADMIN_ID}")
        return message.from_user.id == ADMIN_ID
