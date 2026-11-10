"""Q3: whether late shipments come from promising or from shipping."""

import matplotlib.pyplot as plt
import pandas as pd

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
        None. Writes ``docs/figures/q3_late_by_promise.png``.
    """
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.bar(
        by_window.index,
        by_window["late_rate"] * 100,
        color=plotting.CRITICAL,
        width=0.72,
    )
    ax.set_title("Share of orders shipped late, by promised lead time")
    ax.set_xlabel("Promised lead time (days between order and required date)")
    ax.set_ylabel("Orders shipped late (%)")
    ax.set_ylim(0, 105)
    ax.axvline(6, color=plotting.BASELINE, linewidth=1, linestyle="--")
    ax.annotate(
        "actual median time to ship (6 days)",
        (6, 97),
        xytext=(8, 0),
        textcoords="offset points",
        fontsize=9,
        color=plotting.INK_SECONDARY,
    )
    plotting.save(fig, "q3_late_by_promise.png")


def plot_actual_days(df):
    """Plot the distribution of actual order-to-shipment time.

    Args:
        df (pandas.DataFrame): Output of :func:`load_shipments`;
            values above 30 days are clipped into the last bin.

    Returns:
        None. Writes ``docs/figures/q3_actual_days.png``.
    """
    fig, ax = plt.subplots(figsize=(8, 3.8))
    ax.hist(
        df["actual_days"].clip(upper=30),
        bins=range(0, 31),
        color=plotting.SERIES[0],
        rwidth=0.9,
    )
    ax.set_title("Actual time from order to shipment")
    ax.set_xlabel("Days from order to shipment (30 = 30 or more)")
    ax.set_ylabel("Orders")
    plotting.save(fig, "q3_actual_days.png")


def main():
    """Print fulfillment statistics and write both Q3 figures.

    Args:
        None.

    Returns:
        None. Prints to stdout and writes two PNGs.
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
