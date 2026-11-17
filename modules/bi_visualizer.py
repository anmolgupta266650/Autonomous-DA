import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go


COLOR_THEMES = {
    "Cyber Indigo (Default)": px.colors.qualitative.Plotly,
    "Vibrant Neon": px.colors.qualitative.Bold,
    "Emerald & Teal": px.colors.sequential.Teal,
    "Sunset & Amber": px.colors.sequential.Sunsetdark,
    "Cool Blues & Ice": px.colors.sequential.Blues_r,
    "Prism Dynamic": px.colors.qualitative.Prism,
    "Pastel Clean": px.colors.qualitative.Pastel
}


def build_bi_chart(
    df: pd.DataFrame,
    chart_type: str,
    x_col: str,
    y_col: str = None,
    color_col: str = None,
    size_col: str = None,
    aggregation: str = "Sum",
    orientation: str = "Vertical",
    barmode: str = "group",
    theme_name: str = "Cyber Indigo (Default)",
    title: str = "",
    agg_method: str = None,
    agg_func: str = None,
    **kwargs
):
    """
    Builds a Tableau / Power BI caliber interactive chart based on user configurations.
    """
    if df is None or df.empty or not x_col:
        return None

    if agg_method:
        aggregation = agg_method.capitalize()
    elif agg_func:
        aggregation = agg_func.capitalize()

    df_plot = df.copy()
    color_seq = COLOR_THEMES.get(theme_name, px.colors.qualitative.Plotly)

    # Clean up title
    if not title:
        title = f"{chart_type}: {y_col if y_col else 'Count'} by {x_col}"

    try:
        # Aggregation Logic
        if chart_type in ["Bar Chart", "Line Chart", "Area Chart", "Treemap", "Pie / Donut Chart", "Sunburst"]:
            if y_col and y_col in df_plot.columns and pd.api.types.is_numeric_dtype(df_plot[y_col]):
                group_cols = [x_col]
                if color_col and color_col != "None" and color_col in df_plot.columns and color_col != x_col:
                    group_cols.append(color_col)

                agg_map = {
                    "Sum": "sum",
                    "Average": "mean",
                    "Count": "count",
                    "Median": "median",
                    "Min": "min",
                    "Max": "max",
                    "Std Dev": "std"
                }
                agg_func = agg_map.get(aggregation, "sum")
                
                # Perform group by
                df_grouped = df_plot.groupby(group_cols, as_index=False)[y_col].agg(agg_func)
                df_grouped[y_col] = df_grouped[y_col].round(2)
                plot_data = df_grouped
            else:
                # Count aggregation
                group_cols = [x_col]
                if color_col and color_col != "None" and color_col in df_plot.columns and color_col != x_col:
                    group_cols.append(color_col)
                plot_data = df_plot.groupby(group_cols, as_index=False).size().rename(columns={"size": "Record_Count"})
                y_col = "Record_Count"
        else:
            plot_data = df_plot

        # Render Chart Types
        if chart_type == "Bar Chart":
            is_horiz = orientation == "Horizontal"
            x_arg = y_col if is_horiz else x_col
            y_arg = x_col if is_horiz else y_col
            
            fig = px.bar(
                plot_data,
                x=x_arg,
                y=y_arg,
                color=color_col if color_col and color_col != "None" else None,
                barmode=barmode,
                orientation="h" if is_horiz else "v",
                color_discrete_sequence=color_seq,
                text_auto=True,
                title=title
            )

        elif chart_type == "Line Chart":
            fig = px.line(
                plot_data,
                x=x_col,
                y=y_col,
                color=color_col if color_col and color_col != "None" else None,
                markers=True,
                color_discrete_sequence=color_seq,
                title=title
            )

        elif chart_type == "Area Chart":
            fig = px.area(
                plot_data,
                x=x_col,
                y=y_col,
                color=color_col if color_col and color_col != "None" else None,
                color_discrete_sequence=color_seq,
                title=title
            )

        elif chart_type == "Scatter / Bubble Plot":
            fig = px.scatter(
                plot_data,
                x=x_col,
                y=y_col,
                color=color_col if color_col and color_col != "None" else None,
                size=size_col if size_col and size_col != "None" and pd.api.types.is_numeric_dtype(plot_data[size_col]) else None,
                color_discrete_sequence=color_seq,
                marginal_x="histogram",
                marginal_y="box",
                title=title
            )

        elif chart_type == "Pie / Donut Chart":
            # Donut chart uses hole=0.4
            fig = px.pie(
                plot_data,
                names=x_col,
                values=y_col,
                color=x_col,
                hole=0.42,
                color_discrete_sequence=color_seq,
                title=title
            )
            fig.update_traces(textposition="inside", textinfo="percent+label")

        elif chart_type == "Box Plot":
            fig = px.box(
                plot_data,
                x=x_col,
                y=y_col,
                color=color_col if color_col and color_col != "None" else None,
                points="outliers",
                color_discrete_sequence=color_seq,
                title=title
            )

        elif chart_type == "Violin Plot":
            fig = px.violin(
                plot_data,
                x=x_col,
                y=y_col,
                color=color_col if color_col and color_col != "None" else None,
                box=True,
                points="all",
                color_discrete_sequence=color_seq,
                title=title
            )

        elif chart_type == "Histogram":
            fig = px.histogram(
                plot_data,
                x=x_col,
                color=color_col if color_col and color_col != "None" else None,
                marginal="rug",
                color_discrete_sequence=color_seq,
                title=title
            )

        elif chart_type == "Treemap":
            path_cols = [x_col]
            if color_col and color_col != "None" and color_col != x_col:
                path_cols.append(color_col)
            fig = px.treemap(
                plot_data,
                path=path_cols,
                values=y_col,
                color=y_col,
                color_continuous_scale="Viridis",
                title=title
            )

        elif chart_type == "Sunburst":
            path_cols = [x_col]
            if color_col and color_col != "None" and color_col != x_col:
                path_cols.append(color_col)
            fig = px.sunburst(
                plot_data,
                path=path_cols,
                values=y_col,
                color=y_col,
                color_continuous_scale="Purples",
                title=title
            )

        else:
            return None

        # Dark Glassmorphic layout polish
        fig.update_layout(
            template="plotly_dark",
            paper_bgcolor="rgba(0,0,0,0)",
            plot_bgcolor="rgba(15, 23, 42, 0.4)",
            font=dict(family="Plus Jakarta Sans, sans-serif", color="#e2e8f0"),
            title_font=dict(size=18, color="#f8fafc"),
            legend=dict(
                bgcolor="rgba(15, 23, 42, 0.6)",
                bordercolor="rgba(255,255,255,0.1)",
                borderwidth=1
            ),
            margin=dict(l=30, r=30, t=55, b=40)
        )
        return fig

    except Exception as e:
        return None


def build_executive_dashboard_charts(df: pd.DataFrame):
    """
    Automatically creates a cohesive 4-chart Executive Dashboard Grid and 4 summary KPIs
    tailored to the active dataset (Power BI / Tableau Executive View).
    """
    if df is None or df.empty:
        return {}, []

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()

    # Determine primary metric
    primary_num = None
    priority_keywords = ["sales", "profit", "charges", "value", "revenue", "cost", "income", "amount", "total", "tuition", "chance", "gpa", "score"]
    for kw in priority_keywords:
        for col in num_cols:
            if kw in col.lower():
                primary_num = col
                break
        if primary_num:
            break
    if not primary_num and num_cols:
        primary_num = num_cols[0]

    # Secondary metric
    secondary_num = None
    for col in num_cols:
        if col != primary_num and not col.lower().endswith("id"):
            secondary_num = col
            break

    # Determine primary category
    primary_cat = None
    for col in cat_cols:
        if not col.lower().endswith("id") and df[col].nunique() <= 20:
            primary_cat = col
            break
    if not primary_cat and cat_cols:
        primary_cat = cat_cols[0]

    # Secondary category
    secondary_cat = None
    for col in cat_cols:
        if col != primary_cat and not col.lower().endswith("id") and df[col].nunique() <= 10:
            secondary_cat = col
            break

    # Date column
    date_col = None
    for col in df.columns:
        if "date" in col.lower() or "time" in col.lower() or pd.api.types.is_datetime64_any_dtype(df[col]):
            date_col = col
            break

    charts = {}

    # 1. Bar Chart: Primary Category vs Primary Metric
    if primary_cat and primary_num:
        grouped = df.groupby(primary_cat, as_index=False)[primary_num].sum().sort_values(by=primary_num, ascending=False).head(10)
        fig_bar = px.bar(
            grouped,
            x=primary_cat,
            y=primary_num,
            color=primary_cat,
            color_discrete_sequence=px.colors.qualitative.Bold,
            text_auto=".2s",
            title=f"Total {primary_num} by {primary_cat}"
        )
        fig_bar.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15, 23, 42, 0.4)")
        charts["cat_bar"] = fig_bar

    # 2. Trend / Distribution Chart
    if date_col and primary_num:
        try:
            df_temp = df.copy()
            df_temp["_date_parsed"] = pd.to_datetime(df_temp[date_col], errors="coerce")
            trend_df = df_temp.dropna(subset=["_date_parsed"]).sort_values(by="_date_parsed")
            trend_grouped = trend_df.groupby(pd.Grouper(key="_date_parsed", freq="ME"))[primary_num].sum().reset_index()
            fig_trend = px.line(
                trend_grouped,
                x="_date_parsed",
                y=primary_num,
                markers=True,
                title=f"Monthly {primary_num} Trajectory Over Time"
            )
            fig_trend.update_traces(line_color="#38bdf8", fill="tozeroy", fillcolor="rgba(56, 189, 248, 0.1)")
            fig_trend.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15, 23, 42, 0.4)")
            charts["trend"] = fig_trend
        except Exception:
            pass

    if "trend" not in charts and primary_num:
        # Fallback to distribution histogram with density
        fig_dist = px.histogram(
            df,
            x=primary_num,
            marginal="box",
            nbins=30,
            color_discrete_sequence=["#06b6d4"],
            title=f"Distribution Profile: {primary_num}"
        )
        fig_dist.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15, 23, 42, 0.4)")
        charts["trend"] = fig_dist

    # 3. Donut Chart: Composition & Share
    donut_cat = secondary_cat if secondary_cat else primary_cat
    if donut_cat:
        if primary_num:
            pie_data = df.groupby(donut_cat, as_index=False)[primary_num].sum().sort_values(by=primary_num, ascending=False).head(7)
            val_col = primary_num
        else:
            pie_data = df[donut_cat].value_counts().head(7).reset_index()
            pie_data.columns = [donut_cat, "Count"]
            val_col = "Count"

        fig_donut = px.pie(
            pie_data,
            names=donut_cat,
            values=val_col,
            hole=0.45,
            color_discrete_sequence=px.colors.qualitative.Prism,
            title=f"Share of {val_col} by {donut_cat}"
        )
        fig_donut.update_traces(textposition="inside", textinfo="percent+label")
        fig_donut.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15, 23, 42, 0.4)")
        charts["donut"] = fig_donut

    # 4. Multi-variable Relationship (Scatter or Treemap)
    if primary_num and secondary_num:
        fig_scatter = px.scatter(
            df,
            x=primary_num,
            y=secondary_num,
            color=primary_cat if primary_cat else None,
            trendline="ols",
            color_discrete_sequence=px.colors.qualitative.Safe,
            title=f"Correlation Analysis: {primary_num} vs. {secondary_num}"
        )
        fig_scatter.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15, 23, 42, 0.4)")
        charts["scatter"] = fig_scatter
    elif primary_cat and primary_num:
        fig_tree = px.treemap(
            df,
            path=[primary_cat],
            values=primary_num,
            color=primary_num,
            color_continuous_scale="Teal",
            title=f"Hierarchy Treemap: {primary_cat}"
        )
        fig_tree.update_layout(template="plotly_dark", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(15, 23, 42, 0.4)")
        charts["scatter"] = fig_tree

    # Executive KPI Summary Cards
    kpis = []
    if primary_num:
        tot = df[primary_num].sum()
        avg = df[primary_num].mean()
        kpis.append({"label": f"Aggregate {primary_num}", "val": f"{tot:,.2f}" if tot > 1000 else f"{tot:.2f}", "sub": "Total Cumulative"})
        kpis.append({"label": f"Average {primary_num}", "val": f"{avg:,.2f}", "sub": "Per Record Mean"})

    kpis.append({"label": "Total Observations", "val": f"{len(df):,}", "sub": "Verified Rows"})
    if primary_cat:
        kpis.append({"label": f"Unique {primary_cat}", "val": f"{df[primary_cat].nunique()}", "sub": "Active Entities"})

    return charts, kpis
