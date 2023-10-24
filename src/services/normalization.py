import logging

import pandas as pd

from services.entries import Entry

logger = logging.getLogger(__name__)


async def get_normalized_entries(entries: list[Entry]):
    df = pd.DataFrame(entries)
    # when you have
    #
    #   drink 100ml
    #   drink 250ml
    #   herbs 1g
    #   herbs 1.5g
    #
    # the plot becomes unreadable because scaling is absolute.
    # so this normalization applies relative category scaling to each type of substance.
    df["normalized_size"] = df.groupby("substance")["amount"].transform(
        lambda s: s / max(1, s.mean())
    )
    return df
