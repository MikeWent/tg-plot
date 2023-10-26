import logging

from pyrogram import client

from services.settings import settings

logger = logging.getLogger(__name__)


async def get_telegram_client() -> client.Client | None:
    if (
        settings.telegram_api_id
        and settings.telegram_api_hash
        and settings.app_name
        and settings.app_data_dir
    ):
        tg = client.Client(
            settings.app_name,
            api_id=settings.telegram_api_id,
            api_hash=settings.telegram_api_hash,
            workdir=settings.app_data_dir,
        )
        return tg
