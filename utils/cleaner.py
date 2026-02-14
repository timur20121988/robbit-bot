import asyncio
from aiogram import types
import logging

async def delete_msg(message: types.Message, delay: int = 30):
    """Wait for 'delay' seconds and then delete the message."""
    await asyncio.sleep(delay)
    try:
        await message.delete()
    except Exception as e:
        logging.warning(f"Failed to delete message {message.message_id}: {e}")

def schedule_deletion(message: types.Message, delay: int = 30):
    """Schedule background deletion of a message."""
    if message:
        asyncio.create_task(delete_msg(message, delay))
