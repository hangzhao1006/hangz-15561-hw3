"""Q1: which customer markets grow or decline, 2013-2022."""

import matplotlib.pyplot as plt
import pandas as pd

import db
import plotting

# 2012 starts in July and 2023 ends in October, so only complete years
# are comparable year over year.
FIRST_FULL_YEAR = 2013
LAST_FULL_YEAR = 2022

SQL = """
SELECT CAST(strftime('%Y', o.OrderDate) AS INTEGER) AS year,
       c.Country AS country,
       SUM(d.UnitPrice * d.Quantity * (1 - d.Discount)) AS revenue
FROM Orders o
JOIN "Order Details" d ON d.OrderID = o.OrderID
JOIN Customers c ON c.CustomerID = o.CustomerID
GROUP BY year, country
"""


def load_market_revenue():
    """Load annual revenue per customer country, complete years only.

    Args:
        None.

    Returns:
        pandas.DataFrame: One row per (year, country) with columns
            ``year`` (int), ``country`` (str) and ``revenue`` (float,
            discounted dollars), limited to 2013-2022.
    """
    df = db.query(SQL)
    df = df[(df["year"] >= FIRST_FULL_YEAR) & (df["year"] <= LAST_FULL_YEAR)]
    return df


def growth_table(df):
    """Compute per-country growth between the first and last two years.

    Args:
        df (pandas.DataFrame): Output of :func:`load_market_revenue`.

    Returns:
        pandas.DataFrame: Indexed by country, sorted by ``cagr``
            descending, with columns ``total_revenue`` (float, dollars
            over all years), ``start_avg`` (float, mean annual revenue
            2013-14), ``end_avg`` (float, mean annual revenue 2021-22)
            and ``cagr`` (float, compound annual growth rate between
            the two window midpoints as a fraction).
    """
    total = df.groupby("country")["revenue"].sum()
    first = df[df["year"] <= FIRST_FULL_YEAR + 1].groupby("country")["revenue"].mean()
    last = df[df["year"] >= LAST_FULL_YEAR - 1].groupby("country")["revenue"].mean()
    n_years = LAST_FULL_YEAR - FIRST_FULL_YEAR - 1  # between the two window midpoints
    cagr = (last / first) ** (1 / n_years) - 1
    out = pd.DataFrame(
        {"total_revenue": total, "start_avg": first, "end_avg": last, "cagr": cagr}
    ).dropna()
    return out.sort_values("cagr", ascending=False)


def plot_top_market_trends(df, top_n=4):
    """Plot annual revenue lines for the largest markets.

    Args:
        df (pandas.DataFrame): Output of :func:`load_market_revenue`.
        top_n (int): How many markets to draw, ranked by total
            revenue; capped at 4 by the palette.

    Returns:
        None. Writes ``docs/figures/q1_market_trends.png``.
    """
    top = (
        df.groupby("country")["revenue"].sum().sort_values(ascending=False).head(top_n)
    )
    fig, ax = plt.subplots(figsize=(8, 4.5))
    for color, country in zip(plotting.SERIES, top.index):
        series = df[df["country"] == country].set_index("year")["revenue"] / 1e6
        ax.plot(series.index, series.values, color=color, label=country)
        ax.annotate(
            country,
            (series.index[-1], series.values[-1]),
            xytext=(6, 0),
            textcoords="offset points",
            va="center",
            fontsize=9.5,
            color=color,
            fontweight="bold",
        )
    ax.set_title("Annual revenue in the four largest markets")
    ax.set_ylabel("Revenue (million $)")
    ax.set_xlabel("Order year")
    ax.set_ylim(bottom=0)
    ax.set_xticks(range(FIRST_FULL_YEAR, LAST_FULL_YEAR + 1))
    ax.legend(loc="lower left", ncol=4)
    ax.margins(x=0.02)
    fig.subplots_adjust(right=0.88)
    plotting.save(fig, "q1_market_trends.png")


def plot_growth_ranking(growth, min_revenue=1e7):
    """Plot a CAGR bar ranking of sufficiently large markets.

    Args:
        growth (pandas.DataFrame): Output of :func:`growth_table`.
        min_revenue (float): Minimum total revenue in dollars for a
            market to appear.

    Returns:
        None. Writes ``docs/figures/q1_growth_ranking.png``.
    """
    g = growth[growth["total_revenue"] >= min_revenue].sort_values("cagr")
    colors = [plotting.SERIES[0] if v >= 0 else plotting.CRITICAL for v in g["cagr"]]
    fig, ax = plt.subplots(figsize=(8, 0.34 * len(g) + 1.2))
    ax.barh(g.index, g["cagr"] * 100, color=colors, height=0.62)
    ax.axvline(0, color=plotting.BASELINE, linewidth=1)
    ax.set_title("Revenue growth by market, 2013–14 vs 2021–22 (CAGR)")
    ax.set_xlabel("Compound annual growth rate (%)")
    ax.grid(axis="y", visible=False)
    for y, (country, row) in enumerate(g.iterrows()):
        ax.annotate(
            f"{row['cagr'] * 100:+.1f}%",
            (row["cagr"] * 100, y),
            xytext=(5 if row["cagr"] >= 0 else -5, 0),
            textcoords="offset points",
            va="center",
            ha="left" if row["cagr"] >= 0 else "right",
            fontsize=8.5,
            color=plotting.INK_SECONDARY,
        )
    ax.margins(x=0.15)
    plotting.save(fig, "q1_growth_ranking.png")


def main():
    """Print the market growth table and write both Q1 figures.

    Args:
        None.

    Returns:
        None. Prints to stdout and writes two PNGs.
    """
    plotting.setup()
    df = load_market_revenue()
    growth = growth_table(df)

    pd.set_option("display.float_format", lambda v: f"{v:,.3f}")
    print(f"Markets with >= $10M total revenue ({FIRST_FULL_YEAR}-{LAST_FULL_YEAR}):")
    big = growth[growth["total_revenue"] >= 1e7]
    print(big.assign(cagr_pct=big["cagr"] * 100).round(1))

    plot_top_market_trends(df)
    plot_growth_ranking(growth)


if __name__ == "__main__":
    main()
