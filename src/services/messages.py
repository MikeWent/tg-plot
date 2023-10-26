import logging

from cache import AsyncTTL
from pyrogram import client, types

from services.settings import settings

logger = logging.getLogger(__name__)


@AsyncTTL(time_to_live=120)
async def get_messages(tg: client.Client) -> list[types.Message]:
    async with tg:
        messages = []
        async for msg in tg.get_chat_history(chat_id=settings.telegram_channel_id, limit=100):  # type: ignore
            if hasattr(msg, "text") and msg.text:
                messages.append(msg)
        return messages
