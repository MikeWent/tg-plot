import logging
import re
from dataclasses import dataclass
from datetime import datetime

from telethon import types

logger = logging.getLogger(__name__)


@dataclass
class Entry:
    date: datetime
    substance: str
    amount: float = 1.00


def make_entry(original_message: types.Message, line: str) -> Entry | None:
    # 12:34 herbs 1.25g
    #                       xx:xx
    #                       |       not spaces
    #                       |       |    optional space
    #                       |       |    |  anything
    #                       |       |    |  |
    #                       \/      \/   \/ \/
    match = re.findall(r"(..:..) ([^\s]+) ?(.*)", line)
    logger.debug("text: '%s', match: %s" % (line, match))
    if not match:
        return
    exact_time, substance, amount = match[0]
    # convert amount to number without units
    if amount:
        try:
            # match only digits, dots and commas
            digits = re.findall(r"[\d\.,]*", amount)
            if digits:
                # 1.25gr -> 1.25
                amount = float(digits[0])
        except ValueError:
            logger.debug("unable to convert '%s' to number" % amount)
            amount = 1.00
    else:
        amount = 1.00

    return Entry(
        date=original_message.date,  # type: ignore
        substance=substance,
        amount=amount,
    )


async def get_entries(messages: list[types.Message]) -> list[Entry]:
    entries = []
    for message in messages:
        if not message.message or not message.date:
            continue
        logger.debug(message.message)
        for line in message.message.splitlines():
            entry = make_entry(
                original_message=message,
                line=line,
            )
            if entry:
                entries.append(entry)
    return entries
