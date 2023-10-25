import logging

from cache import AsyncTTL
from pyrogram import client, types

from services.settings import settings

logger = logging.getLogger(__name__)

# telegram client
tg = client.Client(
    settings.app_name,
    api_id=settings.telegram_api_id,
    api_hash=settings.telegram_api_hash,
    workdir=settings.app_data_dir,
)


@AsyncTTL(time_to_live=120)
async def get_messages() -> list[types.Message]:
    async with tg:
        messages = []
        async for msg in tg.get_chat_history(chat_id=settings.telegram_channel_id, limit=100):  # type: ignore
            if hasattr(msg, "text") and msg.text:
                messages.append(msg)
        return messages
