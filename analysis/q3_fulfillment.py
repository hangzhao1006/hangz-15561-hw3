"""Q3: whether late shipments come from promising or from shipping."""

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


def late_by_promised_window(df, max_days=35):
    """Aggregate the late rate by promised lead time.

    Args:
        df (pandas.DataFrame): Output of :func:`load_shipments`.
        max_days (int): Longest promised lead time kept, in days.

    Returns:
        pandas.DataFrame: Indexed by ``promised_days`` with columns
            ``n`` (int, orders) and ``late_rate`` (float, fraction
            shipped late).
    """
    sub = df[df["promised_days"] <= max_days]
    return sub.groupby("promised_days").agg(
        n=("late", "size"), late_rate=("late", "mean")
    )


def plot_late_by_promise(by_window):
    """Plot the late-shipment rate against the promised lead time.

    Args:
        by_window (pandas.DataFrame): Output of
            :func:`late_by_promised_window`.

    Returns:
        None. Writes ``docs/figures/q3_late_by_promise.html``.
    """
    fig = go.Figure(
        go.Bar(
            x=by_window.index,
            y=by_window["late_rate"] * 100,
            marker_color=plotting.CRITICAL,
            customdata=by_window["n"],
            hovertemplate=(
                "promised %{x} days: %{y:.1f}% late (%{customdata} orders)"
                "<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title="Share of orders shipped late, by promised lead time",
        xaxis=dict(
            title="Promised lead time (days between order and required date)",
            showgrid=False,
        ),
        yaxis=dict(title="Orders shipped late (%)", range=[0, 108]),
        bargap=0.28,
    )
    fig.add_vline(
        x=6,
        line_color=plotting.BASELINE,
        line_width=1,
        line_dash="dash",
        annotation_text="actual median time to ship (6 days)",
        annotation_position="top right",
        annotation_font=dict(size=12, color=plotting.INK_SECONDARY),
    )
    plotting.save(fig, "q3_late_by_promise.html", "Q3 · Late by promise")


def plot_actual_days(df):
    """Plot the distribution of actual order-to-shipment time.

    Args:
        df (pandas.DataFrame): Output of :func:`load_shipments`;
            values above 30 days are clipped into the last bin.

    Returns:
        None. Writes ``docs/figures/q3_actual_days.html``.
    """
    days = df["actual_days"].clip(upper=30).astype(int).value_counts().sort_index()
    fig = go.Figure(
        go.Bar(
            x=days.index,
            y=days.values,
            marker_color=plotting.SERIES[0],
            hovertemplate="%{x} days: %{y} orders<extra></extra>",
        )
    )
    fig.update_layout(
        title="Actual time from order to shipment",
        xaxis=dict(
            title="Days from order to shipment (30 = 30 or more)",
            showgrid=False,
        ),
        yaxis=dict(title="Orders"),
        bargap=0.12,
    )
    plotting.save(fig, "q3_actual_days.html", "Q3 · Actual days to ship")


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

    print(f"Shipped orders: {len(df):,}")
    print(f"Overall late rate: {df['late'].mean() * 100:.1f}%")
    print(f"Median actual days to ship: {df['actual_days'].median():.0f}")
    print("\nBy shipper (late % / median days to ship):")
    print(
        df.groupby("shipper")
        .agg(orders=("late", "size"), late_pct=("late", "mean"), med_days=("actual_days", "median"))
        .assign(late_pct=lambda t: (t["late_pct"] * 100).round(1))
    )
    by_window = late_by_promised_window(df)
    fast = df[df["promised_days"] <= 7]
    slow = df[df["promised_days"] >= 29]
    print(f"\nOrders promised in <= 7 days: {len(fast):,}, late rate {fast['late'].mean() * 100:.1f}%")
    print(f"Orders promised in >= 29 days: {len(slow):,}, late rate {slow['late'].mean() * 100:.1f}%")
    print(
        "Median actual days to ship, promised <= 7 vs >= 29: "
        f"{fast['actual_days'].median():.0f} vs {slow['actual_days'].median():.0f}"
    )

    plot_late_by_promise(by_window)
    plot_actual_days(df)


if __name__ == "__main__":
    main()
