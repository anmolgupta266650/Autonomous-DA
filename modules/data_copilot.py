import re
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import Dict, Any, Optional, Tuple


def ask_data_copilot(df: pd.DataFrame, question: str) -> Dict[str, Any]:
    """
    Intelligent plain-English query assistant.
    Interprets natural language queries, aggregates data, and generates responsive charts.
    """
    if df is None or df.empty or not question.strip():
        return {
            "answer": "Please provide a valid dataset and question.",
            "data": None,
            "fig": None
        }

    q = question.lower().strip()
    all_cols = df.columns.tolist()
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()

    # Find mentioned columns
    matched_cols = [c for c in all_cols if c.lower() in q]
    matched_num = [c for c in num_cols if c.lower() in q]
    matched_cat = [c for c in cat_cols if c.lower() in q]

    # Fallbacks if not explicitly mentioned
    target_metric = matched_num[0] if matched_num else (num_cols[0] if num_cols else None)
    target_dim = matched_cat[0] if matched_cat else (cat_cols[0] if cat_cols else None)

    # 1. Row count query
    if any(k in q for k in ["how many", "count", "number of rows", "total records"]):
        if target_dim and any(k in q for k in ["per", "by", "each", "group"]):
            grouped = df[target_dim].value_counts().reset_index()
            grouped.columns = [target_dim, "Record_Count"]
            fig = px.bar(grouped.head(10), x=target_dim, y="Record_Count", title=f"Record Count by {target_dim}", color="Record_Count", color_continuous_scale="Viridis")
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc"))
            return {
                "answer": f"The dataset contains a total of **{len(df):,} records**. Below is the breakdown by **{target_dim}**.",
                "data": grouped.head(15),
                "fig": fig
            }
        return {
            "answer": f"The active dataset contains exactly **{len(df):,} records** across **{len(df.columns)} columns**.",
            "data": None,
            "fig": None
        }

    # 2. Total / Sum query
    if any(k in q for k in ["total", "sum", "overall", "aggregate"]) and target_metric:
        if target_dim and any(k in q for k in ["by", "per", "across", "for each"]):
            grouped = df.groupby(target_dim, as_index=False)[target_metric].sum().sort_values(by=target_metric, ascending=False)
            fig = px.bar(grouped.head(10), x=target_dim, y=target_metric, title=f"Total {target_metric} by {target_dim}", color=target_metric, color_continuous_scale="Blues")
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc"))
            top_val = grouped.iloc[0]
            return {
                "answer": f"The total **{target_metric}** is **{df[target_metric].sum():,.2f}**. The highest category is **{top_val[target_dim]}** with **{top_val[target_metric]:,.2f}**.",
                "data": grouped.head(15),
                "fig": fig
            }
        total_val = df[target_metric].sum()
        return {
            "answer": f"The grand total **{target_metric}** across all active records is **{total_val:,.2f}**.",
            "data": None,
            "fig": None
        }

    # 3. Average / Mean query
    if any(k in q for k in ["average", "mean", "avg"]) and target_metric:
        if target_dim and any(k in q for k in ["by", "per", "across", "for each"]):
            grouped = df.groupby(target_dim, as_index=False)[target_metric].mean().sort_values(by=target_metric, ascending=False)
            fig = px.bar(grouped.head(10), x=target_dim, y=target_metric, title=f"Average {target_metric} by {target_dim}", color=target_metric, color_continuous_scale="Purples")
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc"))
            return {
                "answer": f"The overall average **{target_metric}** is **{df[target_metric].mean():,.2f}**. Below is the average benchmarked across **{target_dim}**.",
                "data": grouped.head(15),
                "fig": fig
            }
        avg_val = df[target_metric].mean()
        return {
            "answer": f"The average **{target_metric}** is **{avg_val:,.2f}** (Median: {df[target_metric].median():,.2f}, Std: {df[target_metric].std():,.2f}).",
            "data": None,
            "fig": None
        }

    # 4. Top-N Rankings query (e.g. "top 5 clients", "highest sales")
    if any(k in q for k in ["top", "highest", "best", "leading", "most", "lowest", "worst"]):
        # Extract number if specified (e.g. top 5, top 10)
        n_match = re.search(r"\b(\d+)\b", q)
        top_n = int(n_match.group(1)) if n_match else 5
        is_lowest = any(k in q for k in ["lowest", "worst", "bottom", "least"])

        if target_dim and target_metric:
            grouped = df.groupby(target_dim, as_index=False)[target_metric].sum().sort_values(by=target_metric, ascending=not is_lowest)
            head_data = grouped.head(top_n)
            color_scale = "Reds" if is_lowest else "Tealgrn"
            fig = px.bar(head_data, x=target_dim, y=target_metric, title=f"{'Bottom' if is_lowest else 'Top'} {top_n} {target_dim} by {target_metric}", color=target_metric, color_continuous_scale=color_scale)
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc"))
            return {
                "answer": f"Here are the **{'lowest' if is_lowest else 'top'} {top_n} {target_dim}** ranked by **{target_metric}**.",
                "data": head_data,
                "fig": fig
            }

    # 5. Correlation / Association query
    if any(k in q for k in ["correlation", "relationship", "correlated", "associated", "versus", "vs"]):
        if len(matched_num) >= 2:
            m1, m2 = matched_num[0], matched_num[1]
        elif len(num_cols) >= 2:
            m1, m2 = num_cols[0], num_cols[1]
        else:
            m1, m2 = None, None

        if m1 and m2:
            corr_val = df[m1].corr(df[m2])
            fig = px.scatter(df, x=m1, y=m2, trendline="ols", title=f"Scatter Plot & Trend: {m1} vs {m2} (r = {corr_val:.3f})")
            fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc"))
            strength = "strong" if abs(corr_val) > 0.7 else "moderate" if abs(corr_val) > 0.4 else "weak"
            direction = "positive" if corr_val > 0 else "negative"
            return {
                "answer": f"The Pearson correlation between **{m1}** and **{m2}** is **{corr_val:.3f}**. This represents a **{strength} {direction}** association.",
                "data": None,
                "fig": fig
            }

    # 6. General Breakdown fallback
    if target_dim and target_metric:
        grouped = df.groupby(target_dim, as_index=False)[target_metric].sum().sort_values(by=target_metric, ascending=False).head(10)
        fig = px.bar(grouped, x=target_dim, y=target_metric, title=f"{target_metric} breakdown by {target_dim}", color=target_metric)
        fig.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", font=dict(color="#f8fafc"))
        return {
            "answer": f"Here is the breakdown of **{target_metric}** across **{target_dim}** based on your question: *'{question}'*.",
            "data": grouped,
            "fig": fig
        }

    return {
        "answer": f"I analyzed your dataset of {len(df):,} records for *'{question}'*. You can ask questions like: *'Who are the top 5 by sales?'*, *'What is average profit by region?'*, or *'What is the correlation between sales and profit?'*.",
        "data": df.head(5),
        "fig": None
    }

