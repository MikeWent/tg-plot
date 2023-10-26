from dataclasses import dataclass
from typing import Annotated

from fastapi import Depends, Form, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from fastapi.security import HTTPBasic, HTTPBasicCredentials

from helpers.flash import FlashMessage, FlashMessageCategory, flash_message
from helpers.settings import settings
from helpers.templates import templates

router = APIRouter()
security = HTTPBasic()


def auth_required(credentials: Annotated[HTTPBasicCredentials, Depends(security)]):
    if settings.admin_password and str(credentials.password) != (
        settings.admin_password
    ):
        raise HTTPException(
            status_code=401,
            headers={"WWW-Authenticate": "Basic"},
        )


@router.get("/", response_class=HTMLResponse)
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


@router.post("/")
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
