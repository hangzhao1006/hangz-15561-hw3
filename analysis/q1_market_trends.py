"""Q1: which customer markets grow or stall, Jul 1996 - May 1998."""

import pandas as pd
import plotly.graph_objects as go

import db
import plotting

# The data covers Jul 1996 - May 1998. The only pair of windows with
# identical month coverage is Jul-May vs Jul-May one year later.
YEAR1 = ("1996-07-01", "1997-06-01")  # Jul 1996 - May 1997
YEAR2 = ("1997-07-01", "1998-06-01")  # Jul 1997 - May 1998

SQL = """
SELECT o.OrderDate AS order_date,
       c.Country AS country,
       SUM(d.UnitPrice * d.Quantity * (1 - d.Discount)) AS revenue
FROM Orders o
JOIN "Order Details" d ON d.OrderID = o.OrderID
JOIN Customers c ON c.CustomerID = o.CustomerID
GROUP BY o.OrderID
"""


def load_market_revenue():
    """Load per-order revenue with order date and customer country.

    Args:
        None.

    Returns:
        pandas.DataFrame: One row per order with columns ``order_date``
            (datetime), ``country`` (str) and ``revenue`` (float,
            discounted dollars).
    """
    df = db.query(SQL)
    df["order_date"] = pd.to_datetime(df["order_date"])
    return df


def growth_table(df):
    """Compute same-month year-over-year growth per country.

    Compares Jul 1996 - May 1997 against Jul 1997 - May 1998, the two
    windows with identical calendar-month coverage, so partial years
    cannot bias the comparison.

    Args:
        df (pandas.DataFrame): Output of :func:`load_market_revenue`.

    Returns:
        pandas.DataFrame: Indexed by country, sorted by ``growth``
            descending, with columns ``total_revenue`` (float, dollars
            over the whole dataset), ``year1`` and ``year2`` (float,
            window revenue in dollars) and ``growth`` (float,
            year-over-year change as a fraction).
    """
    def window(bounds):
        lo, hi = bounds
        sub = df[(df["order_date"] >= lo) & (df["order_date"] < hi)]
        return sub.groupby("country")["revenue"].sum()

    out = pd.DataFrame(
        {
            "total_revenue": df.groupby("country")["revenue"].sum(),
            "year1": window(YEAR1),
            "year2": window(YEAR2),
        }
    ).dropna()
    out["growth"] = out["year2"] / out["year1"] - 1
    return out.sort_values("growth", ascending=False)


def plot_market_race(df):
    """Plot quarterly revenue for the three largest markets.

    Args:
        df (pandas.DataFrame): Output of :func:`load_market_revenue`.

    Returns:
        None. Writes ``docs/figures/q1_market_trends.html``.
    """
    quarterly = (
        df.set_index("order_date")
        .groupby("country")
        .resample("QE")["revenue"]
        .sum()
        .unstack(0)
    ) / 1e3
    quarterly = quarterly.loc[: "1998-03-31"]  # 1998 Q2 has only 5 weeks
    labels = [f"{ts.year} Q{ts.quarter}" for ts in quarterly.index]
    fig = go.Figure()
    for country, color, dash, symbol, yshift in (
        ("USA", plotting.SERIES[0], "solid", "circle", -16),
        ("Germany", plotting.SERIES[1], "solid", "square", 10),
        ("France", plotting.CRITICAL, "dash", "diamond", 0),
    ):
        fig.add_trace(
            go.Scatter(
                x=labels,
                y=quarterly[country],
                name=country,
                mode="lines+markers",
                line=dict(color=color, width=3, dash=dash),
                marker=dict(size=7, symbol=symbol),
                hovertemplate=country + ": $%{y:.1f}K<extra></extra>",
            )
        )
        fig.add_annotation(
            x=labels[-1],
            y=quarterly[country].iloc[-1],
            text=f"<b>{country}</b>",
            showarrow=False,
            xanchor="left",
            xshift=6,
            yshift=yshift,
            font=dict(color=color, size=12),
            bgcolor=plotting.SURFACE,
        )
    fig.update_layout(
        title="The US and Germany pulled away; France stood still",
        hovermode="x unified",
        showlegend=False,
        margin=dict(t=22, r=66),
        xaxis=dict(title="Order quarter", showgrid=False),
        yaxis=dict(title="Quarterly revenue", tickprefix="$", ticksuffix="K",
                   rangemode="tozero"),
    )
    plotting.save(fig, "q1_market_trends.html", "01 · The market race")


def plot_growth_ranking(growth, min_revenue=3e4):
    """Plot same-month YoY revenue growth against a zero baseline.

    Args:
        growth (pandas.DataFrame): Output of :func:`growth_table`.
        min_revenue (float): Minimum total revenue in dollars for a
            market to appear.

    Returns:
        None. Writes ``docs/figures/q1_growth_ranking.html``.
    """
    ranked = growth[growth["total_revenue"] >= min_revenue].sort_values("growth")
    rates = ranked["growth"] * 100
    colors = [plotting.SERIES[0] if rate >= 0 else plotting.CRITICAL for rate in rates]
    fig = go.Figure(
        go.Scatter(
            x=rates,
            y=ranked.index,
            mode="markers+text",
            marker=dict(size=8, color=colors),
            text=[f"{rate:+.0f}%" for rate in rates],
            textposition=["middle right" if rate >= 0 else "middle left" for rate in rates],
            textfont=dict(size=11, color=plotting.INK),
            customdata=ranked["total_revenue"] / 1e3,
            hovertemplate="%{y}<br>%{x:+.0f}% YoY · $%{customdata:.0f}K total<extra></extra>",
        )
    )
    for country, rate, color in zip(ranked.index, rates, colors):
        fig.add_shape(
            type="line", x0=0, x1=rate, y0=country, y1=country,
            line=dict(color=color, width=2), layer="below",
        )
    fig.add_vline(x=0, line_color=plotting.BASELINE, line_width=1, layer="below")
    fig.update_layout(
        title="France, Canada and Denmark sat out the boom",
        xaxis=dict(
            title="Year-over-year revenue change", ticksuffix="%",
            range=[min(0, rates.min()) - 24, max(0, rates.max()) + 24],
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
    print("Markets with >= $30K total revenue, same-month YoY growth:")
    big = growth[growth["total_revenue"] >= 3e4]
    print(big.assign(growth_pct=big["growth"] * 100).round(1))

    plot_market_race(df)
    plot_growth_ranking(growth)


if __name__ == "__main__":
    main()
