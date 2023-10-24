#!/usr/bin/env python3
from datetime import datetime
from os import getenv, remove
import io
import re
import logging
from dataclasses import dataclass

import fastapi
from pyrogram import client, errors, types
from contextlib import asynccontextmanager
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from cache import AsyncTTL

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

import warnings

warnings.simplefilter("ignore", category=FutureWarning)

API_ID = getenv("TELEGRAM_API_ID")
API_HASH = getenv("TELEGRAM_API_HASH")
CHANNEL_ID = getenv("TELEGRAM_CHANNEL_ID")
DATA_DIR = getenv("DATA_DIR") or "./data/"
assert API_ID
assert API_HASH
assert CHANNEL_ID
CHANNEL_ID = int(CHANNEL_ID)

APP_NAME = "tg-plot"


# telegram
tg = client.Client(APP_NAME, api_id=API_ID, api_hash=API_HASH, workdir=DATA_DIR)


@asynccontextmanager
async def lifespan(app: fastapi.FastAPI):
    try:
        await tg.start()
    except errors.AuthKeyUnregistered:
        remove(DATA_DIR + f"/{APP_NAME}.session")
        exit("[!] restart and authorize manually")
    yield
    await tg.stop()


# web server
fastapi_app = fastapi.FastAPI(lifespan=lifespan)
fastapi_app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# global logger
logger = logging.getLogger("uvicorn")


# index
@fastapi_app.get("/")
async def index() -> str:
    return "https://github.com/MikeWent/tg-plot"


@dataclass
class Entry:
    original_text: str
    original_date: datetime

    date: datetime
    substance: str
    amount: float = 1.00


@AsyncTTL(time_to_live=10, maxsize=1)
async def fetch_messages():
    entries = []
    async for message in tg.get_chat_history(chat_id=CHANNEL_ID, limit=100):  # type: ignore
        message: types.Message = message
        if not message.text:
            continue
        for message_line in message.text.splitlines():
            if not message_line:
                continue

            exact_time, substance, amount = "", "", Entry.amount
            # 12:34 herbs 1g
            match = re.findall(r"(..:..) ([^\s]+) ?(.*)", message_line)
            logger.info("message: '%s', match: %s" % (message_line, match))

            # verify that we have a match and 3 groups
            if not len(match) == 1 or not len(groups := match[0]) == 3:
                continue

            # 00:00 smth 1.25gr
            exact_time, substance, amount = groups
            try:
                # 1.25gr -> 1.25
                digits = re.findall(r"[\d\.,]*", amount)
                if digits:
                    amount = float(digits[0])
            except ValueError:
                # whatever, give up
                amount = 1.00

            # entries.append(matches)
            entry = Entry(
                original_date=message.date,
                original_text=message_line,
                date=message.date,
                amount=amount,
                substance=substance,
            )
            entries.append(entry)
    return entries


@fastapi_app.get("/fetch")
async def display_fetched_messages():
    return await fetch_messages()


# plot
@fastapi_app.get("/plot")
async def plot() -> HTMLResponse:
    entries = await fetch_messages()

    # when you have
    #
    #   drink 100ml
    #   drink 250ml
    #   herbs 1g
    #   herbs 1.5g
    #
    # the plot becomes unreadable because scaling is absolute.
    # so this normalization applies relative category scaling to each type of substance.
    df = pd.DataFrame(entries)
    df["normalized_size"] = df.groupby("substance")["amount"].transform(
        lambda s: s / max(1, s.mean())
    )
    logger.info(df)

    # draw the main scatter plot
    fig = px.scatter(
        data_frame=df,
        x="date",
        y="substance",
        color="substance",
        size="normalized_size",
        hover_name="substance",
        hover_data="original_text",
    )
    # add timeline and period selectors
    fig.update_xaxes(
        dtick="H12",
        rangeslider_visible=True,
        rangeselector=dict(
            buttons=list(
                [
                    dict(count=1, label="1D", step="day", stepmode="backward"),
                    dict(count=7, label="7D", step="day", stepmode="backward"),
                    dict(count=1, label="1M", step="month", stepmode="todate"),
                    dict(step="all"),
                ]
            )
        ),
    )
    # draw overall usage as background histogram
    fig.add_trace(
        go.Histogram(
            name="all",
            x=df["date"],
            y=df["normalized_size"],
            xbins=dict(size="D1"),
            opacity=0.15,
        )
    )

    # output HTML
    buffer = io.StringIO()
    fig.write_html(
        file=buffer,
        include_plotlyjs="cdn",
        full_html=False,
    )
    html = buffer.getvalue().encode()

    return HTMLResponse(content=html)
