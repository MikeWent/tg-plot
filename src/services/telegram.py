import logging

from telethon import TelegramClient

from errors import SettingsAreEmpty, TelegramNotAuthorized
from helpers.settings import settings

logger = logging.getLogger(__name__)

tg: TelegramClient | None = None


async def get_telegram_client(for_login_process: bool = False) -> TelegramClient:
    tg = await get_base_telegram_client()
    await tg.connect()
    if not await tg.is_user_authorized():
        tg.disconnect()
        raise TelegramNotAuthorized
    return tg


async def get_base_telegram_client():
    global tg

    if (
        not settings.app_name
        or not settings.telegram_api_id
        or not settings.telegram_api_hash
        or not settings.telegram_channel_id
        or not settings.app_data_dir
    ):
        raise SettingsAreEmpty

    if not tg:
        tg = TelegramClient(
            session=settings.app_data_dir + "/" + settings.app_name,
            api_id=settings.telegram_api_id,
            api_hash=settings.telegram_api_hash,
        )

    return tg
