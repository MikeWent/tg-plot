#!/usr/bin/env python3
import logging
from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from fastapi import Depends, FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.sessions import SessionMiddleware

from services.entries import get_entries
from services.messages import get_messages
from services.normalization import get_normalized_entries
from services.plot import get_plot_html
from services.settings import settings
from services.telegram import get_telegram_client

logger = logging.getLogger(__name__)

# web
fastapi_app = FastAPI()
fastapi_app.add_middleware(SessionMiddleware, secret_key=settings.app_secret_key)
fastapi_app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
security = HTTPBasic()


# web flash message functionality
class FlashMessageCategory(str, Enum):
    error = "❌"
    warning = "⚠️"
    info = "ℹ️"
    success = "✅"


@dataclass
class FlashMessage:
    category: FlashMessageCategory
    title: str | None = None
    text: str | None = None


def flash_message(request: Request, message: FlashMessage) -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append(message.__dict__)


def get_flashed_messages(request: Request):
    messages = request.session.pop("_messages", [])
    messages = [FlashMessage(**x) for x in messages]
    return messages


templates.env.globals["get_flashed_messages"] = get_flashed_messages
templates.env.globals["settings"] = settings


# index
@fastapi_app.get("/")
async def index():
    return RedirectResponse(url="/plot")


# plot
@fastapi_app.get("/plot", response_class=HTMLResponse)
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


# settings
def auth_required(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    if settings.admin_password and str(credentials.password) != (
        settings.admin_password
    ):
        raise HTTPException(
            status_code=401,
            headers={"WWW-Authenticate": "Basic"},
        )


@fastapi_app.get("/settings", response_class=HTMLResponse)
async def show_settings(request: Request, auth=Depends(auth_required)):
    return templates.TemplateResponse(
        name="settings.jinja2", context=dict(request=request, settings=settings)
    )


@dataclass
class SubmittedSettings:
    telegram_api_id: int | None = Form(None)
    telegram_api_hash: str | None = Form(None)
    telegram_channel_id: str | None = Form(None)
    admin_password: str | None = Form(None)


@fastapi_app.post("/settings")
async def update_settings(
    request: Request,
    submitted_settings: SubmittedSettings = Depends(),
    auth=Depends(auth_required),
):
    settings.__dict__.update(submitted_settings.__dict__)
    settings.save()
    flash_message(
        request=request,
        message=FlashMessage(
            category=FlashMessageCategory.success,
            title="Settings updated",
        ),
    )
    return await show_settings(request=request)
