import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from typing import List, Dict, Tuple, Optional


def generate_pivot_table(
    df: pd.DataFrame,
    index_cols: List[str],
    column_cols: Optional[List[str]],
    value_col: str,
    agg_func: str = "sum",
    add_margins: bool = True
) -> pd.DataFrame:
    """
    Creates an Excel & Power BI style dynamic multi-dimensional pivot table.
    Supports multi-level index rows, columns, and grand total margins.
    Guaranteed to prevent 'Grouper not 1-dimensional' by isolating value columns from dimensions.
    """
    if df is None or df.empty or not index_cols or not value_col:
        return pd.DataFrame()

    work = df.loc[:, ~df.columns.duplicated()].copy()

    # Ensure value_col is strictly excluded from index_cols and column_cols
    clean_index = [c for c in index_cols if c != value_col and c in work.columns]
    if not clean_index:
        return pd.DataFrame()

    clean_columns = None
    if column_cols:
        clean_columns = [c for c in column_cols if c != value_col and c not in clean_index and c in work.columns]
        if len(clean_columns) == 0:
            clean_columns = None

    # Ensure numeric aggregation on value column
    work[value_col] = pd.to_numeric(work[value_col], errors="coerce").fillna(0)

    agg_map = {
        "sum": "sum",
        "mean": "mean",
        "average": "mean",
        "count": "count",
        "min": "min",
        "max": "max",
        "median": "median",
        "std": "std"
    }
    actual_agg = agg_map.get(agg_func.lower(), "sum")

    try:
        pivot = pd.pivot_table(
            work,
            values=value_col,
            index=clean_index,
            columns=clean_columns,
            aggfunc=actual_agg,
            fill_value=0,
            margins=add_margins,
            margins_name="Total"
        )

        if isinstance(pivot, pd.Series):
            pivot = pivot.to_frame()

        # Flatten multi-index columns to clean strings to prevent Streamlit warnings/errors
        if isinstance(pivot.columns, pd.MultiIndex):
            pivot.columns = [" - ".join(str(c) for c in col if str(c) != "") for col in pivot.columns]
        else:
            pivot.columns = [str(c) for c in pivot.columns]

        return pivot.round(2)
    except Exception as e:
        print(f"Error generating pivot table: {e}")
        return pd.DataFrame()


def compute_dax_measures(
    df: pd.DataFrame,
    dimension_col: str,
    metric_col: str,
    measure_type: str,
    date_col: Optional[str] = None
) -> Tuple[pd.DataFrame, str]:
    """
    Computes industry-standard Power BI DAX-style measures:
    - % Contribution to Total: [Metric] / CALCULATE(SUM([Metric]), ALL())
    - Cumulative Running Total: Running YTD sum across ordered dimension/date
    - Moving Average: 3-period rolling average smoothing
    - Growth Rate (Period-over-Period % change)
    """
    if df is None or df.empty or dimension_col not in df.columns or metric_col not in df.columns:
        return pd.DataFrame(), "Invalid dimension or metric column."

    work = df[[dimension_col, metric_col] + ([date_col] if date_col and date_col in df.columns else [])].dropna().copy()
    work[metric_col] = pd.to_numeric(work[metric_col], errors="coerce").fillna(0)

    if date_col and date_col in work.columns:
        work["_dt"] = pd.to_datetime(work[date_col], errors="coerce")
        work = work.sort_values("_dt")
        grouped = work.groupby(dimension_col, as_index=False)[metric_col].sum()
    else:
        grouped = work.groupby(dimension_col, as_index=False)[metric_col].sum().sort_values(metric_col, ascending=False)

    col_name = ""
    if measure_type == "contribution_pct":
        col_name = f"{metric_col}_%_Contribution"
        total = grouped[metric_col].sum()
        grouped[col_name] = ((grouped[metric_col] / total) * 100).round(2)
        desc = f"DAX: DIVIDE(SUM({metric_col}), CALCULATE(SUM({metric_col}), ALL('{dimension_col}')))"

    elif measure_type == "running_total":
        col_name = f"{metric_col}_Cumulative_YTD"
        grouped[col_name] = grouped[metric_col].cumsum().round(2)
        desc = f"DAX: CALCULATE(SUM({metric_col}), FILTER(ALL('{dimension_col}'), '{dimension_col}' <= MAX('{dimension_col}')))"

    elif measure_type == "moving_avg":
        col_name = f"{metric_col}_3Period_MovingAvg"
        grouped[col_name] = grouped[metric_col].rolling(window=3, min_periods=1).mean().round(2)
        desc = f"DAX: AVERAGEX(DATESINPERIOD(Calendar[Date], LASTDATE(Calendar[Date]), -3, MONTH), {metric_col})"

    elif measure_type == "growth_rate":
        col_name = f"{metric_col}_Growth_Rate_%"
        grouped[col_name] = (grouped[metric_col].pct_change() * 100).fillna(0).round(2)
        desc = f"DAX: DIVIDE({metric_col} - CALCULATE({metric_col}, DATEADD(Date, -1, YEAR)), CALCULATE({metric_col}, DATEADD(Date, -1, YEAR)))"

    else:
        col_name = metric_col
        desc = f"SUM({metric_col})"

    return grouped, desc


def build_powerbi_matrix_chart(summary_df: pd.DataFrame, dim_col: str, metric_col: str, measure_col: Optional[str] = None) -> go.Figure:
    """
    Renders a Power BI styled dual-axis card and bar chart.
    """
    if summary_df is None or summary_df.empty or dim_col not in summary_df.columns or metric_col not in summary_df.columns:
        return go.Figure()

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=summary_df[dim_col],
        y=summary_df[metric_col],
        name=metric_col,
        marker=dict(color="#3b82f6", line=dict(color="#1d4ed8", width=1.5)),
        opacity=0.85
    ))

    if measure_col and measure_col in summary_df.columns and measure_col != metric_col:
        fig.add_trace(go.Scatter(
            x=summary_df[dim_col],
            y=summary_df[measure_col],
            name=measure_col,
            mode="lines+markers",
            yaxis="y2",
            line=dict(color="#f59e0b", width=3),
            marker=dict(size=8, color="#d97706")
        ))

        fig.update_layout(
            yaxis2=dict(
                title=dict(text=str(measure_col), font=dict(color="#f59e0b")),
                tickfont=dict(color="#f59e0b"),
                overlaying="y",
                side="right",
                gridcolor="rgba(255, 255, 255, 0.05)"
            )
        )

    fig.update_layout(
        title=f"<b>Power BI Measure Visualizer: {metric_col} by {dim_col}</b>",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc", family="Inter, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=420,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig

