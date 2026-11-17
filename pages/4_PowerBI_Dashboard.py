import streamlit as st
import pandas as pd
from modules.common_ui import render_sidebar_data_controls, render_page_header
from modules.bi_visualizer import build_bi_chart, build_executive_dashboard_charts, COLOR_THEMES
from modules.data_loader import get_dataset_metadata

working_df = render_sidebar_data_controls()
render_page_header("🖥️ Power BI Executive Dashboard", working_df)

meta = get_dataset_metadata(working_df)

st.markdown("### 🖥️ Executive Business Intelligence Dashboard")
st.caption("Multi-visual analytics dashboard matching Power BI and Tableau executive capabilities.")

exec_charts, exec_kpis = build_executive_dashboard_charts(working_df)

if exec_kpis:
    kpi_cols = st.columns(len(exec_kpis))
    for idx, kpi in enumerate(exec_kpis):
        with kpi_cols[idx]:
            st.markdown(f"""
            <div class="kpi-box">
                <div class="kpi-label">{kpi['label']}</div>
                <div class="kpi-number">{kpi['val']}</div>
                <div class="kpi-subtext highlight">{kpi['sub']}</div>
            </div>
            """, unsafe_allow_html=True)

st.write("")

dash_row1_col1, dash_row1_col2 = st.columns(2)
with dash_row1_col1:
    if "cat_bar" in exec_charts:
        st.plotly_chart(exec_charts["cat_bar"], width="stretch")
with dash_row1_col2:
    if "trend" in exec_charts:
        st.plotly_chart(exec_charts["trend"], width="stretch")

dash_row2_col1, dash_row2_col2 = st.columns(2)
with dash_row2_col1:
    if "donut" in exec_charts:
        st.plotly_chart(exec_charts["donut"], width="stretch")
with dash_row2_col2:
    if "scatter" in exec_charts:
        st.plotly_chart(exec_charts["scatter"], width="stretch")

st.markdown("---")

with st.expander("🎨 Custom Visual Builder (Design Any Custom Chart)", expanded=False):
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        custom_chart_type = st.selectbox(
            "Chart Type",
            ["Bar Chart", "Line Chart", "Area Chart", "Scatter / Bubble Plot", "Pie / Donut Chart", "Box Plot", "Violin Plot", "Histogram", "Treemap", "Sunburst"],
            key="custom_chart_type",
            help="Pick the visual representation that best communicates your data."
        )
    with c2:
        custom_x = st.selectbox("X-Axis Dimension", working_df.columns.tolist(), key="custom_x", help="The primary horizontal axis dimension or category.")
    with c3:
        num_opts = ["None"] + meta.get("numeric_cols", [])
        custom_y = st.selectbox("Y-Axis Metric", num_opts, index=1 if len(num_opts) > 1 else 0, key="custom_y", help="The numeric metric to plot along the vertical axis.")
        actual_y = None if custom_y == "None" else custom_y
    with c4:
        custom_agg = st.selectbox("Aggregation", ["Sum", "Average", "Count", "Median", "Min", "Max", "Std Dev"], key="custom_agg", help="The mathematical aggregation rule.")

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        custom_color = st.selectbox("Legend / Hue", ["None"] + working_df.columns.tolist(), key="custom_color", help="Categorical column to color-code traces.")
    with c6:
        custom_size = st.selectbox("Bubble Size (Scatter)", ["None"] + meta.get("numeric_cols", []), key="custom_size", help="Numeric column to size scatter bubbles.")
    with c7:
        custom_theme = st.selectbox("Color Palette", list(COLOR_THEMES.keys()), key="custom_theme")
    with c8:
        custom_title = st.text_input("Chart Title", f"{custom_chart_type}: {custom_x}", key="custom_title")

    custom_fig = build_bi_chart(
        df=working_df,
        chart_type=custom_chart_type,
        x_col=custom_x,
        y_col=actual_y,
        color_col=custom_color,
        size_col=custom_size,
        aggregation=custom_agg,
        theme_name=custom_theme,
        title=custom_title
    )
    if custom_fig:
        st.plotly_chart(custom_fig, width="stretch")

