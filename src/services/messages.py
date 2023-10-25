import logging
from os import getenv

from cache import AsyncTTL
from pyrogram import client, types

logger = logging.getLogger(__name__)

API_ID = getenv("TELEGRAM_API_ID")
API_HASH = getenv("TELEGRAM_API_HASH")
DATA_DIR = getenv("DATA_DIR") or "./data/"
CHANNEL_ID = getenv("TELEGRAM_CHANNEL_ID")

assert API_ID
assert API_HASH
assert CHANNEL_ID
CHANNEL_ID = int(CHANNEL_ID)
APP_NAME = "tg-plot"

# telegram client
tg = client.Client(APP_NAME, api_id=API_ID, api_hash=API_HASH, workdir=DATA_DIR)


@AsyncTTL(time_to_live=120)
async def get_messages() -> list[types.Message]:
    async with tg:
        messages = []
        async for msg in tg.get_chat_history(chat_id=CHANNEL_ID, limit=100):  # type: ignore
            if hasattr(msg, "text") and msg.text:
                messages.append(msg)
        return messages
