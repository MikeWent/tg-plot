import logging

from telethon import TelegramClient, types

from helpers.settings import settings

logger = logging.getLogger(__name__)


async def get_messages(tg: TelegramClient) -> list[types.Message]:
    async with tg:
        messages = []
        async for msg in tg.iter_messages(entity=types.PeerChannel(channel_id=settings.telegram_channel_id), limit=100):  # type: ignore
            if hasattr(msg, "message") and msg.message:
                messages.append(msg)
        return messages
