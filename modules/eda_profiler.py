import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


def get_detailed_statistics(df: pd.DataFrame):
    """
    Computes extended statistical metrics for numeric columns:
    mean, std, min, 25%, 50%, 75%, max, skewness, kurtosis, variance.
    """
    numeric_df = df.select_dtypes(include=[np.number])
    if numeric_df.empty:
        return pd.DataFrame()

    stats_list = []
    for col in numeric_df.columns:
        series = numeric_df[col].dropna()
        if len(series) == 0:
            continue
        stats_list.append({
            "Column": col,
            "Count": int(series.count()),
            "Mean": round(float(series.mean()), 2),
            "Std Dev": round(float(series.std()), 2) if len(series) > 1 else 0.0,
            "Min": round(float(series.min()), 2),
            "25% (Q1)": round(float(series.quantile(0.25)), 2),
            "Median (Q2)": round(float(series.median()), 2),
            "75% (Q3)": round(float(series.quantile(0.75)), 2),
            "Max": round(float(series.max()), 2),
            "Skewness": round(float(series.skew()), 2) if len(series) > 2 else 0.0,
            "Kurtosis": round(float(series.kurtosis()), 2) if len(series) > 3 else 0.0
        })

    return pd.DataFrame(stats_list)


def plot_missing_values(df: pd.DataFrame):
    """
    Creates an interactive bar chart of missing values by column.
    """
    null_counts = df.isnull().sum()
    null_pct = (null_counts / len(df) * 100).round(2)
    missing_df = pd.DataFrame({
        "Column": null_counts.index,
        "Missing_Count": null_counts.values,
        "Missing_Pct": null_pct.values
    }).sort_values(by="Missing_Count", ascending=False)

    missing_df = missing_df[missing_df["Missing_Count"] > 0]

    if missing_df.empty:
        return None

    fig = px.bar(
        missing_df,
        x="Column",
        y="Missing_Count",
        text="Missing_Pct",
        color="Missing_Pct",
        color_continuous_scale="Reds",
        title="Missing Values by Column (Count & % of Total)",
        labels={"Missing_Count": "Missing Records", "Missing_Pct": "Missing %"}
    )
    fig.update_traces(texttemplate='%{text}%', textposition='outside')
    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(30,41,59,0.5)",
        font=dict(family="Plus Jakarta Sans, sans-serif"),
        margin=dict(l=20, r=20, t=50, b=30)
    )
    return fig


def plot_correlation_heatmap(df: pd.DataFrame, method="pearson"):
    """
    Generates an interactive Plotly correlation heatmap for numeric features.
    """
    num_df = df.select_dtypes(include=[np.number])
    if num_df.shape[1] < 2:
        return None, pd.DataFrame()

    corr = num_df.corr(method=method).round(2)

    fig = go.Figure(
        data=go.Heatmap(
            z=corr.values,
            x=corr.columns,
            y=corr.columns,
            colorscale="RdBu_r",
            zmin=-1,
            zmax=1,
            text=corr.values,
            texttemplate="%{text}",
            hoverongaps=False
        )
    )
    fig.update_layout(
        title=f"{method.capitalize()} Correlation Heatmap",
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(30,41,59,0.5)",
        font=dict(family="Plus Jakarta Sans, sans-serif"),
        height=520,
        margin=dict(l=20, r=20, t=50, b=30)
    )

    # Extract top correlated pairs (excluding diagonal)
    pairs = []
    cols = corr.columns.tolist()
    for i in range(len(cols)):
        for j in range(i + 1, len(cols)):
            c1, c2 = cols[i], cols[j]
            val = corr.loc[c1, c2]
            pairs.append({"Feature 1": c1, "Feature 2": c2, "Correlation": val, "Abs_Corr": abs(val)})

    pairs_df = pd.DataFrame(pairs).sort_values(by="Abs_Corr", ascending=False).drop(columns=["Abs_Corr"])

    return fig, pairs_df


def plot_feature_distribution(df: pd.DataFrame, column: str):
    """
    Plots the distribution of a single feature:
    Histogram + Boxplot for numeric, Bar chart for categorical.
    """
    if column not in df.columns:
        return None

    if pd.api.types.is_numeric_dtype(df[column]):
        fig = px.histogram(
            df,
            x=column,
            marginal="box",
            nbins=35,
            color_discrete_sequence=["#38bdf8"],
            title=f"Distribution & Spread: {column}"
        )
    else:
        top_cats = df[column].value_counts().head(20).reset_index()
        top_cats.columns = [column, "Frequency"]
        fig = px.bar(
            top_cats,
            x=column,
            y="Frequency",
            color="Frequency",
            color_continuous_scale="Purples",
            title=f"Frequency Breakdown: {column} (Top 20 Categories)"
        )

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(30,41,59,0.5)",
        font=dict(family="Plus Jakarta Sans, sans-serif"),
        margin=dict(l=20, r=20, t=50, b=30)
    )
    return fig
