#!/usr/bin/env python3
from enum import Enum
import logging
from dataclasses import dataclass
from os import getenv
import fastapi
from cache import AsyncTTL

from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse, StreamingResponse
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from services.entries import get_entries
from services.messages import get_messages
from services.normalization import get_normalized_entries

from services.plot import get_plot


APP_SECRET_KEY = getenv("APP_SECRET_KEY")
assert APP_SECRET_KEY

logger = logging.getLogger(__name__)

# web
fastapi_app = fastapi.FastAPI()
fastapi_app.add_middleware(SessionMiddleware, secret_key=APP_SECRET_KEY)
fastapi_app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


# web flash message functionality
class FlashMessageCategory(str, Enum):
    error = "error"
    warning = "warning"
    info = "info"
    success = "success"


@dataclass
class FlashMessage:
    category: FlashMessageCategory
    title: str
    text: str


def flash(request: fastapi.Request, message: FlashMessage) -> None:
    if "_messages" not in request.session:
        request.session["_messages"] = []
    request.session["_messages"].append(message.__dict__)


def get_flashed_messages(request: fastapi.Request):
    messages = request.session.pop("_messages", [])
    messages = [FlashMessage(**x) for x in messages]
    return messages


templates.env.globals["get_flashed_messages"] = get_flashed_messages


# index
@fastapi_app.get("/")
async def index() -> str:
    return "https://github.com/MikeWent/tg-plot"


# plot


@fastapi_app.get("/plot")
async def plot(request: fastapi.Request) -> StreamingResponse:
    async def progressive_html():
        # send start of HTML so browser could start drawing elements
        yield """
        <html>
            <head>
                <style>
                    body {font-size: 1rem; font-family: monospace}
                    .log{margin: 1rem}
                </style>
            </head>
            </body>
                <div class="log">
        """

        br = "<br>\n"
        yield "connecting to telegram..." + br
        messages = []
        async for msg in await get_messages():
            messages.append(msg)
            yield msg.text + br

        yield "parsing messages..." + br
        entries = await get_entries(messages)

        yield "normalizing data..." + br
        data = await get_normalized_entries(entries)

        yield "drawing a plot..." + br
        plot = await get_plot(data)

        # hide the log
        yield """
                </div>
                <style>.log{display:none}</style>
        """
        yield plot
        yield """
            </body>
        </html>"""

    return StreamingResponse(progressive_html(), media_type="text/html")


@fastapi_app.get("/messages", response_class=HTMLResponse)
async def get_all_messages(request: fastapi.Request):
    return templates.TemplateResponse(name="base.jinja2", context=dict(request=request))


@fastapi_app.post("/messages")
async def add_new_message(request: fastapi.Request, message: FlashMessage):
    flash(request=request, message=message)
