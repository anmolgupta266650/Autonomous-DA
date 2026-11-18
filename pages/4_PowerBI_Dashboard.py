import streamlit as st
import pandas as pd
from modules.common_ui import render_sidebar_data_controls, render_page_header
from modules.bi_visualizer import build_bi_chart, build_executive_dashboard_charts, COLOR_THEMES
from modules.powerbi_excel_studio import (
    generate_pivot_table, compute_dax_measures, build_powerbi_matrix_chart
)
from modules.data_loader import get_dataset_metadata

working_df = render_sidebar_data_controls()
render_page_header("🖥️ Power BI & Pivot Matrix Studio", working_df)

meta = get_dataset_metadata(working_df)

st.markdown("### 🖥️ Power BI & Dynamic Pivot Matrix Studio")
st.caption("Enterprise multi-visual dashboards, multi-level pivot tables, and DAX-style measures matching Power BI & Tableau.")

tab_exec, tab_pivot, tab_dax = st.tabs([
    "📊 Executive Dashboard & Visuals",
    "🔲 Multi-Dimensional Pivot Matrix",
    "📐 Power BI DAX Measures"
])

# ==============================================================
# TAB 1: EXECUTIVE DASHBOARD & VISUALS
# ==============================================================
with tab_exec:
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
            st.plotly_chart(exec_charts["cat_bar"], width="stretch", key="dash_cat_bar_plot")
    with dash_row1_col2:
        if "trend" in exec_charts:
            st.plotly_chart(exec_charts["trend"], width="stretch", key="dash_trend_plot")

    dash_row2_col1, dash_row2_col2 = st.columns(2)
    with dash_row2_col1:
        if "donut" in exec_charts:
            st.plotly_chart(exec_charts["donut"], width="stretch", key="dash_donut_plot")
    with dash_row2_col2:
        if "scatter" in exec_charts:
            st.plotly_chart(exec_charts["scatter"], width="stretch", key="dash_scatter_plot")

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
            st.plotly_chart(custom_fig, width="stretch", key="dash_custom_builder_plot")


# ==============================================================
# TAB 2: MULTI-DIMENSIONAL PIVOT MATRIX
# ==============================================================
with tab_pivot:
    st.markdown("##### 🔲 Multi-Level Dynamic Pivot Matrix")
    num_choices = meta.get("numeric_cols", [])
    all_cols = working_df.columns.tolist()

    pv_c1, pv_c2, pv_c3, pv_c4 = st.columns(4)

    with pv_c3:
        val_col = st.selectbox(
            "Aggregated Metric (Value)",
            num_choices if num_choices else all_cols,
            index=0 if num_choices else 0,
            key="pbi_studio_pivot_val",
            help="The numeric metric to aggregate inside the pivot cells."
        )

    dim_candidates = [c for c in all_cols if c != val_col]

    with pv_c1:
        default_rows = [dim_candidates[0]] if dim_candidates else []
        row_dims = st.multiselect(
            "Row Dimensions (Hierarchy)",
            dim_candidates,
            default=default_rows,
            key="pbi_studio_pivot_rows",
            help="Categories to display as row groupings."
        )

    with pv_c2:
        remaining_dims = [c for c in dim_candidates if c not in row_dims]
        default_cols = [remaining_dims[0]] if remaining_dims else []
        col_dims = st.multiselect(
            "Column Dimension (Optional)",
            remaining_dims,
            default=default_cols,
            key="pbi_studio_pivot_cols",
            help="Optional category to pivot horizontally across columns."
        )

    with pv_c4:
        agg_method = st.selectbox(
            "Calculation",
            ["Sum", "Average", "Count", "Min", "Max", "Median", "Std"],
            key="pbi_studio_pivot_agg",
            help="Aggregation function."
        )

    add_totals = st.checkbox(
        "Include Grand Total Margins",
        value=True,
        key="pbi_studio_pivot_totals",
        help="Appends grand total rows and columns to the pivot matrix."
    )

    if row_dims and val_col:
        try:
            pivot_res = generate_pivot_table(working_df, row_dims, col_dims, val_col, agg_func=agg_method, add_margins=add_totals)
            if not pivot_res.empty:
                st.dataframe(pivot_res, width="stretch", key="pbi_studio_pivot_df")
                csv_bytes = pivot_res.to_csv().encode("utf-8")
                st.download_button("📥 Download Pivot Matrix (.csv)", data=csv_bytes, file_name="Dynamic_Pivot_Matrix.csv", mime="text/csv", key="dl_pivot_matrix_btn")
            else:
                st.warning("Could not compute pivot table with the current column selections.")
        except Exception as exc:
            st.warning(f"Pivot table calculation error: {exc}")
    else:
        st.info("Please select at least one Row Dimension and a Metric.")


# ==============================================================
# TAB 3: POWER BI DAX MEASURES
# ==============================================================
with tab_dax:
    st.markdown("##### 📐 Power BI DAX-Style Measure Engine")
    num_choices = meta.get("numeric_cols", [])
    cat_choices = working_df.columns.tolist()

    if num_choices and cat_choices:
        dax_c1, dax_c2, dax_c3 = st.columns(3)
        with dax_c1:
            dax_dim = st.selectbox("Target Dimension", cat_choices, key="pbi_dax_dim")
        with dax_c2:
            dax_metric = st.selectbox("Base Numeric Metric", num_choices, key="pbi_dax_metric")
        with dax_c3:
            dax_type = st.selectbox(
                "DAX Measure Pattern",
                ["contribution_pct", "running_total", "moving_avg", "growth_rate"],
                format_func=lambda x: {
                    "contribution_pct": "% Contribution to Total (ALL)",
                    "running_total": "Cumulative Running Total (YTD)",
                    "moving_avg": "3-Period Rolling Moving Average",
                    "growth_rate": "Period-over-Period Growth Rate %"
                }[x],
                key="pbi_dax_type",
                help="Industry standard DAX formula pattern to calculate across the dimension."
            )

        date_candidates = [c for c in working_df.columns if "date" in c.lower() or pd.api.types.is_datetime64_any_dtype(working_df[c])]
        dax_date = date_candidates[0] if date_candidates else None

        try:
            dax_df, dax_formula = compute_dax_measures(working_df, dax_dim, dax_metric, dax_type, dax_date)
            st.info(f"💡 **Equivalent Power BI DAX Formula**: `{dax_formula}`")

            matrix_fig = build_powerbi_matrix_chart(dax_df, dax_dim, dax_metric, dax_df.columns[-1])
            st.plotly_chart(matrix_fig, width="stretch", key="pbi_dax_matrix_plot")
            st.dataframe(dax_df, width="stretch", key="pbi_dax_table_view")
        except Exception as e:
            st.warning(f"Could not compute DAX measure for selected columns: {e}")
    else:
        st.info("Numeric metrics are required to calculate DAX measures.")
