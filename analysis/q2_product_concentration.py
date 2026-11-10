"""Q2: how concentrated revenue is across the product catalog."""

import matplotlib.pyplot as plt
import numpy as np

import db
import plotting

SQL = """
SELECT p.ProductName AS product,
       cat.CategoryName AS category,
       SUM(d.UnitPrice * d.Quantity * (1 - d.Discount)) AS revenue
FROM "Order Details" d
JOIN Products p ON p.ProductID = d.ProductID
JOIN Categories cat ON cat.CategoryID = p.CategoryID
GROUP BY p.ProductID
ORDER BY revenue DESC
"""


def load_product_revenue():
    """Load lifetime revenue per product, ranked best first.

    Args:
        None.

    Returns:
        pandas.DataFrame: One row per product, sorted by revenue
            descending, with columns ``product`` (str), ``category``
            (str), ``revenue`` (float, discounted dollars), ``share``
            (float, fraction of total) and ``cum_share`` (float,
            cumulative fraction).
    """
    df = db.query(SQL)
    df["share"] = df["revenue"] / df["revenue"].sum()
    df["cum_share"] = df["share"].cumsum()
    return df


def plot_top_products(df, top_n=10):
    """Plot a bar ranking of the best-selling products.

    Args:
        df (pandas.DataFrame): Output of :func:`load_product_revenue`.
        top_n (int): How many products to show.

    Returns:
        None. Writes ``docs/figures/q2_top_products.png``.
    """
    top = df.head(top_n).iloc[::-1]
    fig, ax = plt.subplots(figsize=(8, 4.8))
    ax.barh(top["product"], top["revenue"] / 1e6, color=plotting.SERIES[0], height=0.62)
    for y, (_, row) in enumerate(top.iterrows()):
        ax.annotate(
            f"{row['share'] * 100:.1f}%",
            (row["revenue"] / 1e6, y),
            xytext=(5, 0),
            textcoords="offset points",
            va="center",
            fontsize=8.5,
            color=plotting.INK_SECONDARY,
        )
    ax.set_title("Top 10 products by lifetime revenue (share of company total)")
    ax.set_xlabel("Revenue (million $)")
    ax.grid(axis="y", visible=False)
    ax.margins(x=0.1)
    plotting.save(fig, "q2_top_products.png")


def plot_cumulative_share(df):
    """Plot the cumulative revenue share curve over ranked products.

    Args:
        df (pandas.DataFrame): Output of :func:`load_product_revenue`.

    Returns:
        None. Writes ``docs/figures/q2_cumulative_share.png``.
    """
    n = len(df)
    x = np.arange(1, n + 1)
    fig, ax = plt.subplots(figsize=(8, 4.2))
    ax.plot(x, df["cum_share"] * 100, color=plotting.SERIES[0])
    ax.set_title("Cumulative revenue share of products, ranked best first")
    ax.set_xlabel("Number of products (of 77, best sellers first)")
    ax.set_ylabel("Cumulative share of revenue (%)")
    ax.set_ylim(0, 105)
    ax.set_xlim(0, n + 1)
    for k in (1, 5, 10, 20):
        share = df["cum_share"].iloc[k - 1] * 100
        ax.plot([k], [share], "o", color=plotting.SERIES[0], markersize=8)
        ax.annotate(
            f"top {k}: {share:.0f}%",
            (k, share),
            xytext=(8, -4),
            textcoords="offset points",
            fontsize=9,
            color=plotting.INK_SECONDARY,
        )
    plotting.save(fig, "q2_cumulative_share.png")


def main():
    """Print concentration statistics and write both Q2 figures.

    Args:
        None.

    Returns:
        None. Prints to stdout and writes two PNGs.
    """
    plotting.setup()
    df = load_product_revenue()

    total = df["revenue"].sum()
    print(f"Total product revenue: ${total / 1e6:,.1f}M across {len(df)} products")
    print(f"Top product: {df.iloc[0]['product']} "
          f"(${df.iloc[0]['revenue'] / 1e6:,.1f}M, {df.iloc[0]['share'] * 100:.1f}%)")
    for k in (5, 10, 20):
        print(f"Top {k} products: {df['cum_share'].iloc[k - 1] * 100:.1f}% of revenue")
    print("\nTop 10 products:")
    print(df.head(10)[["product", "category", "revenue", "share"]].round(3))

    plot_top_products(df)
    plot_cumulative_share(df)


if __name__ == "__main__":
    main()
