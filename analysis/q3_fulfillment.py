"""Q3: whether late shipments come from promising or from shipping."""

import numpy as np
import pandas as pd
import plotly.graph_objects as go

import db
import plotting

SQL = """
SELECT o.OrderID,
       s.CompanyName AS shipper,
       julianday(o.RequiredDate) - julianday(o.OrderDate) AS promised_days,
       julianday(o.ShippedDate) - julianday(o.OrderDate) AS actual_days,
       o.ShippedDate > o.RequiredDate AS late
FROM Orders o
JOIN Shippers s ON s.ShipperID = o.ShipVia
WHERE o.ShippedDate IS NOT NULL
"""


def load_shipments():
    """Load one row per shipped order with timing fields.

    Args:
        None.

    Returns:
        pandas.DataFrame: Columns ``OrderID`` (int), ``shipper``
            (str), ``promised_days`` (int, required minus order date),
            ``actual_days`` (float, shipped minus order date) and
            ``late`` (int, 1 if shipped after the required date).
    """
    df = db.query(SQL)
    df["promised_days"] = df["promised_days"].round().astype(int)
    return df


TIER_LABELS = {14: "14 days (rush)", 28: "28 days (standard)", 42: "42 days (flexible)"}


def plot_late_by_promise(df):
    """Compare late-shipment rates across the three promised deadlines.

    The dataset contains exactly three promised lead times: 14, 28 and
    42 days between the order date and the required date.

    Args:
        df (pandas.DataFrame): Output of `load_shipments`.

    Returns:
        None. Writes ``docs/figures/q3_late_by_promise.html``.
    """
    deadline = pd.Categorical(
        df["promised_days"].map(TIER_LABELS),
        categories=list(TIER_LABELS.values()),
        ordered=True,
    )
    groups = df.groupby(deadline, observed=True)["late"].agg(["size", "sum", "mean"])
    rates = groups["mean"] * 100
    fig = go.Figure(
        go.Bar(
            x=rates, y=groups.index, orientation="h",
            name="Late", marker_color=plotting.CRITICAL,
            customdata=groups[["sum", "size"]],
            hovertemplate="%{y} deadline<br>%{customdata[0]:,} of %{customdata[1]:,} orders late<extra></extra>",
        )
    )
    fig.add_trace(
        go.Bar(
            x=100 - rates, y=groups.index, orientation="h",
            name="On time", marker_color="#e7e8df",
            customdata=groups["size"] - groups["sum"],
            hovertemplate="%{y} deadline<br>%{customdata:,} orders on time<extra></extra>",
        )
    )
    for group, rate in rates.items():
        fig.add_annotation(
            x=rate, y=group, xanchor="left", xshift=5,
            text=f"<b>{rate:.1f}% late</b>", showarrow=False,
            font=dict(size=12, color=plotting.INK),
        )
    fig.update_layout(
        title="Rush deadlines are late five times as often",
        barmode="stack", showlegend=False, bargap=0.52,
        xaxis=dict(title="Share of shipped orders", range=[0, 100], dtick=25, ticksuffix="%"),
        yaxis=dict(title="Promised deadline", autorange="reversed", showgrid=False),
        margin=dict(t=20, b=52),
    )
    plotting.save(fig, "q3_late_by_promise.html", "05 · The deadline gap")


def plot_actual_days(fast, slow):
    """Compare the cumulative shares shipped by each elapsed day.

    Args:
        fast (pandas.DataFrame): Orders promised in 14 days (rush).
        slow (pandas.DataFrame): Orders promised in 28 days (standard).

    Returns:
        None. Writes ``docs/figures/q3_actual_days.html``.
    """
    days = np.arange(31)
    fig = go.Figure()
    for group, label, color, dash in (
        (slow, "28-day deadline", plotting.SERIES[0], "solid"),
        (fast, "14-day deadline", plotting.CRITICAL, "dash"),
    ):
        actual = np.sort(group["actual_days"].to_numpy())
        shipped = np.searchsorted(actual, days, side="right") / len(actual) * 100
        fig.add_trace(
            go.Scatter(
                x=days, y=shipped, name=label, mode="lines",
                line=dict(color=color, dash=dash, width=3, shape="hv"),
                hovertemplate=label + ": %{y:.1f}% shipped<extra></extra>",
            )
        )
    midpoint = (fast["actual_days"].median() + slow["actual_days"].median()) / 2
    fig.add_hline(y=50, line_color=plotting.BASELINE, line_dash="dot", line_width=1, layer="below")
    fig.add_annotation(
        x=midpoint, y=50, text=f"<b>Both medians ≈ {midpoint:.0f} days</b>",
        ax=57, ay=37, arrowhead=0, arrowcolor=plotting.BASELINE,
        bgcolor=plotting.SURFACE, font=dict(size=11, color=plotting.INK),
    )
    fig.add_vline(x=14, line_color=plotting.CRITICAL, line_dash="dot", line_width=1,
                  layer="below", annotation_text="rush deadline",
                  annotation_font=dict(size=11, color=plotting.CRITICAL))
    fig.update_layout(
        title="Rush orders shipped no faster than standard ones",
        hovermode="x unified", margin=dict(t=52),
        xaxis=dict(title="Days after order was placed", range=[0, 30], dtick=7, showgrid=False),
        yaxis=dict(title="Orders already shipped", ticksuffix="%", range=[0, 104], dtick=25),
    )
    plotting.save(fig, "q3_actual_days.html", "06 · The fulfillment clock")


def main():
    """Print fulfillment statistics and write both Q3 figures.

    Args:
        None.

    Returns:
        None. Prints to stdout and writes two interactive HTML
        figures.
    """
    plotting.setup()
    df = load_shipments()
    median_days = df["actual_days"].median()

    print(f"Shipped orders: {len(df):,}")
    print(f"Overall late rate: {df['late'].mean() * 100:.1f}%")
    print(f"Median actual days to ship: {median_days:.0f}")
    print("\nBy shipper (late % / median days to ship):")
    print(
        df.groupby("shipper")
        .agg(orders=("late", "size"), late_pct=("late", "mean"), med_days=("actual_days", "median"))
        .assign(late_pct=lambda t: (t["late_pct"] * 100).round(1))
    )
    fast = df[df["promised_days"] == 14]
    slow = df[df["promised_days"] == 28]
    relaxed = df[df["promised_days"] == 42]
    for label, group in (("14 (rush)", fast), ("28 (standard)", slow),
                         ("42 (flexible)", relaxed)):
        print(
            f"Promised {label}: {len(group):,} orders, "
            f"late rate {group['late'].mean() * 100:.1f}%, "
            f"median days to ship {group['actual_days'].median():.0f}"
        )

    plot_late_by_promise(df)
    plot_actual_days(fast, slow)


if __name__ == "__main__":
    main()
