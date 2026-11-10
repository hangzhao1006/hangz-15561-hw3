"""Q1: which customer markets grow or decline, 2013-2022."""

import pandas as pd
import plotly.graph_objects as go

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
        None. Writes ``docs/figures/q1_market_trends.html``.
    """
    top = (
        df.groupby("country")["revenue"].sum().sort_values(ascending=False).head(top_n)
    )
    fig = go.Figure()
    for color, country in zip(plotting.SERIES, top.index):
        series = df[df["country"] == country].set_index("year")["revenue"] / 1e6
        fig.add_trace(
            go.Scatter(
                x=series.index,
                y=series.values,
                name=country,
                mode="lines+markers",
                line=dict(color=color, width=2.4),
                marker=dict(size=6),
                hovertemplate="%{y:.2f}M<extra>" + country + "</extra>",
            )
        )
    fig.update_layout(
        title="Annual revenue in the four largest markets",
        hovermode="x unified",
        xaxis=dict(title="Order year", dtick=1, showgrid=False),
        yaxis=dict(title="Revenue (million $)", rangemode="tozero"),
    )
    plotting.save(fig, "q1_market_trends.html", "Q1 · Market trends")


def plot_growth_ranking(growth, min_revenue=1e7):
    """Plot a CAGR bar ranking of sufficiently large markets.

    Args:
        growth (pandas.DataFrame): Output of :func:`growth_table`.
        min_revenue (float): Minimum total revenue in dollars for a
            market to appear.

    Returns:
        None. Writes ``docs/figures/q1_growth_ranking.html``.
    """
    g = growth[growth["total_revenue"] >= min_revenue].sort_values("cagr")
    colors = [plotting.SERIES[0] if v >= 0 else plotting.CRITICAL for v in g["cagr"]]
    fig = go.Figure(
        go.Bar(
            x=g["cagr"] * 100,
            y=g.index,
            orientation="h",
            marker_color=colors,
            text=[f"{v * 100:+.1f}%" for v in g["cagr"]],
            textposition="outside",
            textfont=dict(size=12, color=plotting.INK_SECONDARY),
            customdata=g["total_revenue"] / 1e6,
            hovertemplate=(
                "%{y}: %{x:+.1f}%/yr · $%{customdata:.0f}M total"
                "<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title="Revenue growth by market, 2013–14 vs 2021–22 (CAGR)",
        xaxis=dict(title="Compound annual growth rate (%)", range=[-4.2, 4.2]),
        yaxis=dict(showgrid=False),
        bargap=0.38,
    )
    fig.add_vline(x=0, line_color=plotting.BASELINE, line_width=1)
    plotting.save(fig, "q1_growth_ranking.html", "Q1 · Growth ranking")


def main():
    """Print the market growth table and write both Q1 figures.

    Args:
        None.

    Returns:
        None. Prints to stdout and writes two interactive HTML
        figures.
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
