from fastapi import Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRouter

from helpers.flash import FlashMessage, FlashMessageCategory, flash_message
from services.entries import get_entries
from services.messages import get_messages
from services.normalization import get_normalized_entries
from services.plot import get_plot_html
from services.telegram import get_telegram_client

router = APIRouter()


# plot
@router.get("/", response_class=HTMLResponse)
async def plot(request: Request):
    telegram_client = await get_telegram_client()
    if not telegram_client:
        flash_message(
            request=request,
            message=FlashMessage(
                category=FlashMessageCategory.warning,
                title="Enter Telegram and Channel settings first",
            ),
        )
        return RedirectResponse(url="/settings")
    messages = await get_messages(telegram_client)
    entries = await get_entries(messages)
    normalized = await get_normalized_entries(entries)
    plot_html = await get_plot_html(normalized)
    return HTMLResponse(content=plot_html)
