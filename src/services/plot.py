import io
import logging
import warnings

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

logger = logging.getLogger(__name__)

warnings.simplefilter("ignore", category=FutureWarning)


async def get_plot_html(data: pd.DataFrame) -> str:
    logger.debug(data)

    # draw the main scatter plot
    fig = px.scatter(
        data_frame=data,
        x="date",
        y="substance",
        color="substance",
        size="normalized_size",
        hover_name="substance",
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
            x=data["date"],
            y=data["normalized_size"],
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
        div_id="plot",
    )
    plot_html = buffer.getvalue()
    return plot_html
