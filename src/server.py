#!/usr/bin/env python3
import logging

from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware

from endpoints.plot import router as plot_router
from endpoints.settings import router as settings_router
from helpers.settings import settings

logger = logging.getLogger(__name__)

# web
fastapi_app = FastAPI()
fastapi_app.add_middleware(SessionMiddleware, secret_key=settings.app_secret_key)
fastapi_app.mount("/static", StaticFiles(directory="static"), name="static")

fastapi_app.include_router(settings_router, prefix="/settings")
fastapi_app.include_router(plot_router, prefix="/plot")


# index
@fastapi_app.get("/")
async def index():
    return RedirectResponse(url="/plot")
