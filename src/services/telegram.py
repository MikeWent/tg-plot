import logging

from telethon import TelegramClient

from errors import SettingsAreEmpty
from helpers.settings import settings

logger = logging.getLogger(__name__)

tg: TelegramClient | None = None


async def get_telegram_client(for_login_process: bool = False) -> TelegramClient:
    if (
        not settings.app_name
        or not settings.telegram_api_id
        or not settings.telegram_api_hash
        or not settings.telegram_channel_id
    ):
        raise SettingsAreEmpty

    global tg
    if not tg:
        tg = TelegramClient(
            session=settings.app_name,
            api_id=settings.telegram_api_id,
            api_hash=settings.telegram_api_hash,
        )

    return tg
