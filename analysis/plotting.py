"""Shared chart style and interactive-figure saving for the analysis."""

import pathlib

import plotly.graph_objects as go
import plotly.io as pio

FIG_DIR = pathlib.Path(__file__).resolve().parent.parent / "docs" / "figures"

# Validated light-mode palette (dataviz reference instance).
SURFACE = "#fffefc"
INK = "#161513"
INK_SECONDARY = "#454340"
MUTED = "#807c75"
GRID = "#e7e3da"
BASELINE = "#c3c2b7"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # blue, orange, aqua, yellow
CRITICAL = "#d03b3b"
GOOD = "#0ca30c"

SANS = '-apple-system, "Helvetica Neue", Arial, sans-serif'
SERIF = 'Georgia, "Times New Roman", serif'

TEMPLATE = go.layout.Template(
    layout=go.Layout(
        paper_bgcolor=SURFACE,
        plot_bgcolor=SURFACE,
        font=dict(family=SANS, size=13, color=INK_SECONDARY),
        title=dict(
            font=dict(family=SERIF, size=19, color=INK),
            x=0,
            xanchor="left",
            pad=dict(l=2),
        ),
        colorway=SERIES,
        xaxis=dict(
            gridcolor=GRID,
            linecolor=BASELINE,
            tickcolor=MUTED,
            tickfont=dict(color=MUTED, size=12),
            title_font=dict(size=13, color=INK_SECONDARY),
            title_standoff=12,
            automargin=True,
            zeroline=False,
        ),
        yaxis=dict(
            gridcolor=GRID,
            linecolor=BASELINE,
            tickcolor=MUTED,
            tickfont=dict(color=MUTED, size=12),
            title_font=dict(size=13, color=INK_SECONDARY),
            title_standoff=10,
            automargin=True,
            zeroline=False,
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.0,
            x=1.0,
            xanchor="right",
            font=dict(size=12),
        ),
        hoverlabel=dict(
            bgcolor="#ffffff",
            bordercolor=BASELINE,
            font=dict(family=SANS, size=13, color=INK),
        ),
        margin=dict(l=10, r=10, t=64, b=48),
    )
)

_PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>html,body{{margin:0;padding:0;background:{surface};height:100%;}}
.chart{{position:absolute;inset:0;}}</style>
</head>
<body><div class="chart">{div}</div></body>
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
    div = fig.to_html(
        full_html=False,
        include_plotlyjs="cdn",
        config={
            "displayModeBar": False,
            "responsive": True,
            "scrollZoom": False,
            "doubleClick": "reset",
        },
        default_width="100%",
        default_height="100%",
    )
    out.write_text(_PAGE.format(title=title, surface=SURFACE, div=div))
    print(f"saved {out.relative_to(FIG_DIR.parent.parent)}")
