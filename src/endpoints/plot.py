from fastapi import Depends, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.routing import APIRouter

from services.entries import get_entries
from services.messages import get_messages
from services.normalization import get_normalized_entries
from services.plot import get_plot_html
from services.telegram import get_telegram_client

from helpers.templates import templates
from helpers.auth import auth_required

router = APIRouter()

cached_plot_html = None


@router.get("/", response_class=HTMLResponse)
async def show_plot(request: Request):
    global cached_plot_html
    if not cached_plot_html:
        telegram_client = await get_telegram_client()
        messages = await get_messages(telegram_client)  # type: ignore
        entries = await get_entries(messages)
        normalized = await get_normalized_entries(entries)
        cached_plot_html = await get_plot_html(normalized)

    return templates.TemplateResponse(
        "plot.jinja2", context=dict(request=request, plot_html=cached_plot_html)
    )


@router.get("/update")
async def update_plot(request: Request, auth=Depends(auth_required)):
    global cached_plot_html
    cached_plot_html = None
    return RedirectResponse("/")
