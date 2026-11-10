"""Shared chart style and figure saving for the analysis scripts."""

import pathlib

import matplotlib as mpl
import matplotlib.pyplot as plt

FIG_DIR = pathlib.Path(__file__).resolve().parent.parent / "docs" / "figures"

# Validated light-mode palette (dataviz reference instance).
SURFACE = "#fcfcfb"
INK = "#0b0b0b"
INK_SECONDARY = "#52514e"
MUTED = "#898781"
GRID = "#e1e0d9"
BASELINE = "#c3c2b7"
SERIES = ["#2a78d6", "#eb6834", "#1baf7a", "#eda100"]  # blue, orange, aqua, yellow
SEQ_BLUE = ["#cde2fb", "#9ec5f4", "#6da7ec", "#3987e5", "#2a78d6", "#256abf", "#184f95"]
CRITICAL = "#d03b3b"
GOOD = "#0ca30c"


def setup():
    """Apply the shared light-mode chart style to matplotlib.

    Args:
        None.

    Returns:
        None. Mutates ``matplotlib.rcParams`` globally.
    """
    mpl.rcParams.update(
        {
            "figure.facecolor": SURFACE,
            "axes.facecolor": SURFACE,
            "savefig.facecolor": SURFACE,
            "font.family": "sans-serif",
            "font.sans-serif": ["Helvetica Neue", "Arial", "DejaVu Sans"],
            "text.color": INK,
            "axes.edgecolor": BASELINE,
            "axes.labelcolor": INK_SECONDARY,
            "axes.titlecolor": INK,
            "axes.titlesize": 13,
            "axes.titleweight": "bold",
            "axes.labelsize": 10.5,
            "axes.grid": True,
            "axes.axisbelow": True,
            "grid.color": GRID,
            "grid.linewidth": 0.8,
            "xtick.color": MUTED,
            "ytick.color": MUTED,
            "xtick.labelsize": 9.5,
            "ytick.labelsize": 9.5,
            "legend.frameon": False,
            "legend.fontsize": 9.5,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.spines.left": False,
            "lines.linewidth": 2,
        }
    )


def save(fig, name):
    """Save a figure into ``docs/figures/`` and close it.

    Args:
        fig (matplotlib.figure.Figure): Figure to write.
        name (str): Output file name, e.g. ``"q1_market_trends.png"``.

    Returns:
        None. Writes the PNG and prints its repo-relative path.
    """
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    out = FIG_DIR / name
    fig.savefig(out, dpi=160, bbox_inches="tight")
    plt.close(fig)
    print(f"saved {out.relative_to(FIG_DIR.parent.parent)}")
