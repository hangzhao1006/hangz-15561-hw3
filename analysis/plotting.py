"""Shared chart style and interactive-figure saving for the analysis."""

import pathlib
from html import escape

import plotly.graph_objects as go
import plotly.io as pio

FIG_DIR = pathlib.Path(__file__).resolve().parent.parent / "docs" / "figures"

SURFACE = "#fffefa"
INK = "#162c31"
INK_SECONDARY = "#384f51"
MUTED = "#506163"
GRID = "#e0e4da"
BASELINE = "#87928c"
SERIES = ["#17685f", "#b25c2c", "#365d9a", "#765485"]
CRITICAL = "#ab4937"

SANS = '-apple-system, "Helvetica Neue", Arial, sans-serif'
TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(family=SANS, size=12, color=INK_SECONDARY),
        colorway=SERIES,
        xaxis=dict(
            gridcolor=GRID,
            linecolor=BASELINE,
            tickcolor=MUTED,
            tickfont=dict(color=MUTED, size=11),
            title_font=dict(size=12, color=INK_SECONDARY),
            title_standoff=8,
            automargin=True,
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor=GRID,
            linecolor=BASELINE,
            tickcolor=MUTED,
            tickfont=dict(color=MUTED, size=11),
            title_font=dict(size=12, color=INK_SECONDARY),
            title_standoff=8,
            automargin=True,
            zeroline=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.0,
            x=0.5,
            xanchor="center",
            font=dict(size=11),
        ),
        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor=BASELINE,
            font=dict(family=SANS, size=13, color=INK),
        ),
        margin=dict(l=12, r=16, t=14, b=45),
    )
)

_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
  html,body{{margin:0;background:{surface};height:100%;}}
  body{{display:grid;grid-template-rows:auto minmax(0,1fr);color:{ink};}}
  header{{margin:15px 16px 5px;}}
  p{{margin:0 0 5px;font:700 9px/1.3 system-ui,sans-serif;
    letter-spacing:.14em;text-transform:uppercase;color:{muted};}}
  h1{{font:400 clamp(18px,4.9vw,25px)/1.13 Georgia,serif;margin:0;text-wrap:balance;}}
  .chart{{min-width:0;min-height:0;}}
</style>
</head>
<body><header><p>{title}</p><h1>{heading}</h1></header><main class="chart">{div}</main></body>
</html>
"""


def setup():
    """Register the shared editorial Plotly template as the default.

    Args:
        None.

    Returns:
        None. Mutates ``plotly.io.templates`` globally.
    """
    pio.templates["editorial"] = TEMPLATE
    pio.templates.default = "editorial"


def save(fig, name, title):
    """Write an interactive figure into ``docs/figures/`` as HTML.

    Args:
        fig (plotly.graph_objects.Figure): Figure to write.
        name (str): Output file name, e.g. ``"q1_market_trends.html"``.
        title (str): Document title for the embedded page.

    Returns:
        None. Writes a self-contained HTML page (plotly.js from CDN)
        and prints its repo-relative path.
    """
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / name
    heading = fig.layout.title.text or title
    fig.update_layout(title_text=None)
    div = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        div_id=out.stem,
        config={
            "displayModeBar": False,
            "responsive": True,
            "scrollZoom": False,
            "doubleClick": "reset",
        },
        default_width="100%",
        default_height="100%",
    )
    out.write_text(
        _PAGE.format(
            title=escape(title), heading=escape(heading), surface=SURFACE,
            ink=INK, muted=MUTED, div=div,
        ),
        encoding="utf-8",
    )
    print(f"saved {out.relative_to(FIG_DIR.parent.parent)}")
