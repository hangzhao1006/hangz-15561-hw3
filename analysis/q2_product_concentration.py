"""Q2: how concentrated revenue is across the product catalog."""

import numpy as np
import plotly.graph_objects as go

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
        None. Writes ``docs/figures/q2_top_products.html``.
    """
    top = df.head(top_n).iloc[::-1]
    fig = go.Figure(
        go.Bar(
            x=top["revenue"] / 1e6,
            y=top["product"],
            orientation="h",
            marker_color=plotting.SERIES[0],
            text=[f"{v * 100:.1f}%" for v in top["share"]],
            textposition="outside",
            textfont=dict(size=12, color=plotting.INK_SECONDARY),
            customdata=top["category"],
            hovertemplate=(
                "%{y} (%{customdata})<br>$%{x:.1f}M · %{text} of total"
                "<extra></extra>"
            ),
        )
    )
    fig.update_layout(
        title="Top 10 products by lifetime revenue (share of company total)",
        xaxis=dict(title="Revenue (million $)", range=[0, 60]),
        yaxis=dict(showgrid=False),
        bargap=0.38,
    )
    plotting.save(fig, "q2_top_products.html", "Q2 · Top products")


def plot_cumulative_share(df):
    """Plot the cumulative revenue share curve over ranked products.

    Args:
        df (pandas.DataFrame): Output of :func:`load_product_revenue`.

    Returns:
        None. Writes ``docs/figures/q2_cumulative_share.html``.
    """
    n = len(df)
    x = np.arange(1, n + 1)
    fig = go.Figure(
        go.Scatter(
            x=x,
            y=df["cum_share"] * 100,
            mode="lines",
            line=dict(color=plotting.SERIES[0], width=2.4),
            customdata=df["product"],
            hovertemplate=(
                "top %{x} products: %{y:.1f}%<br>#%{x}: %{customdata}"
                "<extra></extra>"
            ),
        )
    )
    for k in (1, 5, 10, 20):
        share = df["cum_share"].iloc[k - 1] * 100
        fig.add_trace(
            go.Scatter(
                x=[k],
                y=[share],
                mode="markers+text",
                marker=dict(size=10, color=plotting.SERIES[0]),
                text=[f"top {k}: {share:.0f}%"],
                textposition="middle right",
                textfont=dict(size=12, color=plotting.INK_SECONDARY),
                hoverinfo="skip",
                showlegend=False,
            )
        )
    fig.update_layout(
        title="Cumulative revenue share of products, ranked best first",
        xaxis=dict(title="Number of products (of 77, best sellers first)",
                   range=[0, n + 1]),
        yaxis=dict(title="Cumulative share of revenue (%)", range=[0, 105]),
    )
    plotting.save(fig, "q2_cumulative_share.html", "Q2 · Cumulative share")


def main():
    """Print concentration statistics and write both Q2 figures.

    Args:
        None.

    Returns:
        None. Prints to stdout and writes two interactive HTML
        figures.
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
