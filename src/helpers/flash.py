from dataclasses import dataclass
from enum import Enum

from fastapi import Request


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
