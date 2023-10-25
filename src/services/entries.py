from dataclasses import dataclass
from datetime import datetime
import re
from pyrogram import types

import logging


logger = logging.getLogger(__name__)


@dataclass
class Entry:
    date: datetime
    substance: str
    amount: float = 1.00


async def get_entries(messages: list[types.Message]) -> list[Entry]:
    entries = []
    for message in messages:
        if not message.text:
            continue
        for line in message.text.splitlines():
            # 12:34 herbs 1g
            match = re.findall(r"(..:..) ([^\s]+) ?(.*)", line)
            logger.debug("text: '%s', match: %s" % (line, match))

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
            entries.append(
                Entry(
                    date=message.date,
                    substance=substance,
                    amount=amount,
                )
            )
    return entries
