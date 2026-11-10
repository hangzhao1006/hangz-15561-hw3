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


def plot_market_race(df):
    """Compare annual revenue in the United States and France.

    Args:
        df (pandas.DataFrame): Output of `load_market_revenue`.

    Returns:
        None. Writes ``docs/figures/q1_market_trends.html``.
    """
    annual = df.pivot(index="year", columns="country", values="revenue") / 1e6
    annual = annual[["USA", "France"]].dropna()
    fig = go.Figure()
    for country, color, dash, symbol in (
        ("USA", plotting.CRITICAL, "dash", "square"),
        ("France", plotting.SERIES[0], "solid", "circle"),
    ):
        fig.add_trace(
            go.Scatter(
                x=annual.index,
                y=annual[country],
                name=country,
                mode="lines+markers",
                line=dict(color=color, width=3, dash=dash),
                marker=dict(size=7, symbol=symbol),
                hovertemplate=country + ": $%{y:.2f}M<extra></extra>",
            )
        )

    end = annual.iloc[-1]
    for country, color in (("USA", plotting.CRITICAL), ("France", plotting.SERIES[0])):
        fig.add_annotation(
            x=annual.index[-1],
            y=end[country],
            text=f"<b>{country} · ${end[country]:.2f}M</b>",
            showarrow=False,
            xanchor="right",
            xshift=-4,
            yshift=30 if end[country] == end.max() else -19,
            font=dict(color=color, size=12),
            bgcolor=plotting.SURFACE,
        )
    fig.add_vrect(
        x0=annual.index[-1] - 0.45,
        x1=annual.index[-1] + 0.25,
        fillcolor="#e5ede5",
        opacity=0.85,
        layer="below",
        line_width=0,
    )
    fig.update_layout(
        title="France pulled ahead of the US in 2022",
        hovermode="x unified",
        showlegend=False,
        margin=dict(t=22),
        xaxis=dict(
            title="Order year", tickmode="array", tickvals=[2013, 2017, 2020, 2022],
            range=[annual.index[0] - 0.2, annual.index[-1] + 0.25], showgrid=False,
        ),
        yaxis=dict(
            title="Annual revenue", tickprefix="$", ticksuffix="M", dtick=0.5,
            range=[annual.min().min() - 0.35, annual.max().max() + 0.38],
        ),
    )
    plotting.save(fig, "q1_market_trends.html", "01 · The market shift")


def plot_growth_ranking(growth, min_revenue=1e7):
    """Plot annualized revenue change against a zero-growth baseline.

    Args:
        growth (pandas.DataFrame): Output of `growth_table`.
        min_revenue (float): Minimum total revenue in dollars for a
            market to appear.

    Returns:
        None. Writes ``docs/figures/q1_growth_ranking.html``.
    """
    ranked = growth[growth["total_revenue"] >= min_revenue].sort_values("cagr")
    rates = ranked["cagr"] * 100
    colors = [plotting.SERIES[0] if rate >= 0 else plotting.CRITICAL for rate in rates]
    fig = go.Figure(
        go.Scatter(
            x=rates,
            y=ranked.index,
            mode="markers+text",
            marker=dict(size=8, color=colors),
            text=[f"{rate:+.1f}%" for rate in rates],
            textposition=["middle right" if rate >= 0 else "middle left" for rate in rates],
            textfont=dict(size=11, color=plotting.INK),
            customdata=ranked["total_revenue"] / 1e6,
            hovertemplate="%{y}<br>%{x:+.1f}%/yr · $%{customdata:.1f}M total<extra></extra>",
        )
    )
    for country, rate, color in zip(ranked.index, rates, colors):
        fig.add_shape(
            type="line", x0=0, x1=rate, y0=country, y1=country,
            line=dict(color=color, width=2), layer="below",
        )
    fig.add_vline(x=0, line_color=plotting.BASELINE, line_width=1, layer="below")
    fig.update_layout(
        title="Spain and France lead on growth",
        xaxis=dict(
            title="Annualized revenue change", ticksuffix="%",
            range=[min(0, rates.min()) - 1.7, max(0, rates.max()) + 1.7],
            dtick=2,
        ),
        yaxis=dict(showgrid=False, categoryorder="array", categoryarray=ranked.index),
    )
    plotting.save(fig, "q1_growth_ranking.html", "02 · The growth ranking")


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

    plot_market_race(df)
    plot_growth_ranking(growth)


if __name__ == "__main__":
    main()
