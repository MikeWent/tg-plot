from dataclasses import dataclass

from fastapi import Depends, Form, Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter

from helpers.auth import auth_required, set_password
from helpers.flash import FlashMessage, FlashMessageCategory, flash_message
from helpers.settings import settings
from helpers.templates import templates

router = APIRouter(dependencies=[Depends(auth_required)])


@router.get("/", response_class=HTMLResponse)
async def show_settings(request: Request):
    return templates.TemplateResponse(
        name="settings.jinja2", context=dict(request=request, settings=settings)
    )


@dataclass
class SubmittedSettingsForm:
    telegram_api_id: int | None = Form(None)
    telegram_api_hash: str | None = Form(None)
    telegram_channel_id: int | None = Form(None)
    admin_password: str | None = Form(None)


@router.post("/")
async def update_settings(
    request: Request,
    submitted_settings: SubmittedSettingsForm = Depends(),
):
    if submitted_settings.admin_password:
        set_password(submitted_settings.admin_password)
    settings.update(submitted_settings.__dict__)
    settings.save()
    flash_message(
        request=request,
        message=FlashMessage(
            category=FlashMessageCategory.success,
            title="Settings updated",
        ),
    )
    return await show_settings(request=request)
