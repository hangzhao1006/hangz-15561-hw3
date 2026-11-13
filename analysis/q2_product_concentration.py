"""Q2: how concentrated revenue is across the product catalog."""

from textwrap import wrap

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


def plot_top_products(df):
    """Compare the leading product with the next two products combined.

    Args:
        df (pandas.DataFrame): Output of `load_product_revenue`.

    Returns:
        None. Writes ``docs/figures/q2_top_products.html``.
    """
    top = df.head(3)
    bars = ["Top product", "Nos. 2 + 3", "Nos. 2 + 3"]
    colors = ["#e5b967", "#468676", "#b2d3c3"]
    fig = go.Figure()
    for bar, color, item in zip(bars, colors, top.itertuples()):
        fig.add_trace(
            go.Bar(
                x=[item.revenue / 1e3], y=[bar], orientation="h", name=item.product,
                marker=dict(color=color, line=dict(color=plotting.SURFACE, width=1)),
                hovertemplate=item.product + "<br>$%{x:.1f}K<extra></extra>",
            )
        )
    revenue = top["revenue"] / 1e3
    totals = [revenue.iloc[0], revenue.iloc[1:].sum()]
    for bar, total in zip(bars, totals):
        fig.add_annotation(
            x=total, y=bar, text=f"<b>${total:.0f}K</b>",
            xanchor="left", xshift=5, showarrow=False,
            font=dict(size=12, color=plotting.INK),
        )
    fig.update_layout(
        title="One wine rivals the next two products combined",
        showlegend=False, barmode="stack", bargap=0.47,
        margin=dict(t=15, b=49),
        xaxis=dict(title="Lifetime discounted revenue", tickprefix="$", ticksuffix="K",
                   range=[0, max(totals) * 1.37], nticks=5),
        yaxis=dict(showgrid=False, categoryorder="array", categoryarray=bars[:2][::-1]),
    )
    plotting.save(fig, "q2_top_products.html", "04 · The top seller")


def plot_product_mix(df):
    """Show revenue by product rank in a drillable treemap.

    Args:
        df (pandas.DataFrame): Output of `load_product_revenue`.

    Returns:
        None. Writes ``docs/figures/q2_cumulative_share.html``.
    """
    revenue = df["revenue"] / 1e3
    ids = ["all"]
    parents = [""]
    labels = ["All products"]
    values = [revenue.sum()]
    colors = ["#e6e9df"]
    tiers = (
        (0, 1, df.iloc[0]["product"], "#e5b967"),
        (1, 5, "Ranks 2–5", "#b2d3c3"),
        (5, 20, "Ranks 6–20", "#c5d5e5"),
        (20, len(df), f"Ranks 21–{len(df)}", "#e2e7dd"),
    )
    for start, end, label, color in tiers:
        if start >= end:
            continue
        tier = f"tier-{start + 1}"
        ids.append(tier)
        parents.append("all")
        labels.append(label)
        values.append(revenue.iloc[start:end].sum())
        colors.append(color)
        if start == 0:
            continue
        for rank, item in enumerate(df.iloc[start:end].itertuples(), start=start + 1):
            ids.append(f"product-{rank}")
            parents.append(tier)
            labels.append(item.product)
            values.append(item.revenue / 1e3)
            colors.append(color)

    display_labels = labels.copy()
    display_labels[1] = "<br>".join(wrap(display_labels[1], width=9))
    fig = go.Figure(
        go.Treemap(
            ids=ids, labels=labels, parents=parents, values=values,
            branchvalues="total", maxdepth=2, sort=False,
            marker=dict(colors=colors, line=dict(color=plotting.SURFACE, width=2)),
            tiling=dict(pad=4),
            text=display_labels,
            texttemplate="%{text}<br><b>%{percentRoot:.1%}</b>",
            textfont=dict(size=16, color=plotting.INK),
            pathbar=dict(visible=True, textfont=dict(size=11)),
            hovertemplate="<b>%{label}</b><br>$%{value:.1f}K · %{percentRoot:.1%} of all revenue<extra></extra>",
        )
    )
    fig.update_layout(
        title="Where every $100 of revenue goes",
        margin=dict(l=10, r=10, t=8, b=12),
        uniformtext=dict(minsize=10, mode="hide"),
    )
    plotting.save(fig, "q2_cumulative_share.html", "03 · The product mix")


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
    print(f"Total product revenue: ${total / 1e3:,.1f}K across {len(df)} products")
    print(f"Top product: {df.iloc[0]['product']} "
          f"(${df.iloc[0]['revenue'] / 1e3:,.1f}K, {df.iloc[0]['share'] * 100:.1f}%)")
    for k in (5, 10, 20):
        print(f"Top {k} products: {df['cum_share'].iloc[k - 1] * 100:.1f}% of revenue")
    print("\nTop 10 products:")
    print(df.head(10)[["product", "category", "revenue", "share"]].round(3))

    plot_top_products(df)
    plot_product_mix(df)


if __name__ == "__main__":
    main()
