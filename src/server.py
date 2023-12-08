#!/usr/bin/env python3
import logging

from fastapi import FastAPI, Request
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

import errors
from endpoints.plot import router as plot_router
from endpoints.settings import router as settings_router
from endpoints.telegram import router as telegram_router
from helpers.flash import FlashMessage, FlashMessageCategory, flash_message
from helpers.settings import settings
from helpers.templates import templates

logger = logging.getLogger(__name__)

# web
fastapi_app = FastAPI()
fastapi_app.add_middleware(SessionMiddleware, secret_key=settings.app_secret_key)
fastapi_app.mount("/static", StaticFiles(directory="static"), name="static")

# endpoints
fastapi_app.include_router(settings_router, prefix="/settings")
fastapi_app.include_router(plot_router, prefix="/plot")
fastapi_app.include_router(telegram_router, prefix="/telegram")


# index
@fastapi_app.get("/")
async def index(request: Request):
    return templates.TemplateResponse("index.jinja2", context=dict(request=request))


# exceptions
for error in (errors.TelegramNotAuthorized, errors.SettingsAreEmpty):

    def handler(request: Request, exc: errors.BaseAppException):
        flash_message(
            request=request,
            message=FlashMessage(
                category=FlashMessageCategory.warning,
                title=exc.text,
            ),
        )
        return RedirectResponse(url=exc.redirect_to)

    fastapi_app.add_exception_handler(error, handler)
