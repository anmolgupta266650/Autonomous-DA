import streamlit as st
import pandas as pd
from modules.common_ui import render_sidebar_data_controls, render_page_header
from modules.powerbi_excel_studio import (
    generate_pivot_table, compute_dax_measures, build_powerbi_matrix_chart
)
from modules.data_loader import get_dataset_metadata

working_df = render_sidebar_data_controls()
render_page_header("📊 Excel & Pivot Matrix Studio", working_df)

meta = get_dataset_metadata(working_df)

st.markdown("### 📊 Power BI & Excel Studio: Dynamic Pivot Tables & DAX Measures")
st.caption("Slice, dice, summarize, and compute DAX-style measures across multiple hierarchical dimensions.")

pbi_t1, pbi_t2 = st.tabs(["🔲 Dynamic Multi-Dimensional Pivot Table", "📐 Power BI DAX Measures"])

with pbi_t1:
    st.markdown("##### 🔲 Multi-Level Dynamic Pivot Matrix")
    num_choices = meta.get("numeric_cols", [])
    all_cols = working_df.columns.tolist()

    pv_c1, pv_c2, pv_c3, pv_c4 = st.columns(4)

    with pv_c3:
        val_col = st.selectbox(
            "Aggregated Metric (Value)",
            num_choices if num_choices else all_cols,
            index=0 if num_choices else 0,
            help="The numeric metric to aggregate inside the pivot cells."
        )

    dim_candidates = [c for c in all_cols if c != val_col]

    with pv_c1:
        default_rows = [dim_candidates[0]] if dim_candidates else []
        row_dims = st.multiselect(
            "Row Dimensions (Hierarchy)",
            dim_candidates,
            default=default_rows,
            help="Categories to display as row groupings."
        )

    with pv_c2:
        remaining_dims = [c for c in dim_candidates if c not in row_dims]
        default_cols = [remaining_dims[0]] if remaining_dims else []
        col_dims = st.multiselect(
            "Column Dimension (Optional)",
            remaining_dims,
            default=default_cols,
            help="Optional category to pivot horizontally across columns."
        )

    with pv_c4:
        agg_method = st.selectbox("Calculation", ["Sum", "Average", "Count", "Min", "Max", "Median", "Std"], help="Aggregation function.")

    add_totals = st.checkbox("Include Grand Total Margins", value=True, help="Appends grand total rows and columns to the pivot matrix.")

    if row_dims and val_col:
        try:
            pivot_res = generate_pivot_table(working_df, row_dims, col_dims, val_col, agg_func=agg_method, add_margins=add_totals)
            if not pivot_res.empty:
                st.dataframe(pivot_res, width="stretch")
            else:
                st.warning("Could not compute pivot table with the current column selections.")
        except Exception as exc:
            st.warning(f"Pivot table calculation error: {exc}")
    else:
        st.info("Please select at least one Row Dimension and a Metric.")

with pbi_t2:
    st.markdown("##### 📐 Power BI DAX-Style Measure Engine")
    num_choices = meta.get("numeric_cols", [])
    cat_choices = working_df.columns.tolist()

    if num_choices and cat_choices:
        dax_c1, dax_c2, dax_c3 = st.columns(3)
        with dax_c1:
            dax_dim = st.selectbox("Target Dimension", cat_choices, key="dax_dim")
        with dax_c2:
            dax_metric = st.selectbox("Base Numeric Metric", num_choices, key="dax_metric")
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
                help="Industry standard DAX formula pattern to calculate across the dimension."
            )

        date_candidates = [c for c in working_df.columns if "date" in c.lower() or pd.api.types.is_datetime64_any_dtype(working_df[c])]
        dax_date = date_candidates[0] if date_candidates else None

        try:
            dax_df, dax_formula = compute_dax_measures(working_df, dax_dim, dax_metric, dax_type, dax_date)
            st.info(f"💡 **Equivalent Power BI DAX Formula**: `{dax_formula}`")

            matrix_fig = build_powerbi_matrix_chart(dax_df, dax_dim, dax_metric, dax_df.columns[-1])
            st.plotly_chart(matrix_fig, width="stretch")
            st.dataframe(dax_df, width="stretch")
        except Exception as e:
            st.warning(f"Could not compute DAX measure for selected columns: {e}")
    else:
        st.info("Numeric metrics are required to calculate DAX measures.")

