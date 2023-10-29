from fastapi import Request, Depends, Form
from fastapi.responses import HTMLResponse
from fastapi.routing import APIRouter
from dataclasses import dataclass

from telethon import TelegramClient, errors

from helpers.templates import templates
from helpers.auth import auth_required
from helpers.flash import FlashMessage, FlashMessageCategory, flash_message
from helpers.settings import settings
from services.telegram import get_telegram_client

router = APIRouter(dependencies=[Depends(auth_required)])


@dataclass
class TelegramLoginForm:
    phone: str | None = Form(None)
    code: str | None = Form(None)
    password: str | None = Form(None)


@router.get("/", response_class=HTMLResponse)
async def telegram_auth_page(request: Request):
    return templates.TemplateResponse(
        name="telegram.jinja2", context=dict(request=request, field="phone")
    )


@router.post("/", dependencies=[Depends(auth_required)])
async def telegram_auth_step(
    request: Request,
    form: TelegramLoginForm = Depends(),
    tg: TelegramClient = Depends(get_telegram_client),
):
    field: str | None = None
    success = False
    await tg.connect()

    if form.phone:
        await tg.send_code_request(phone=form.phone)
        field = "code"
    if form.code:
        try:
            await tg.sign_in(code=form.code)
            success = True
        except errors.SessionPasswordNeededError:
            field = "password"
        except errors.BadRequestError:
            field = "code"
    if form.password:
        try:
            await tg.sign_in(
                password=form.password,
            )
            success = True
        except errors.BadRequestError:
            field = "password"

    if success:
        flash_message(
            request=request,
            message=FlashMessage(
                category=FlashMessageCategory.success,
                title="Telegram authenticated",
            ),
        )
        field = None

    return templates.TemplateResponse(
        name="telegram.jinja2", context=dict(request=request, field=field)
    )
