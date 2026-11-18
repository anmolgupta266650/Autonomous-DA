import streamlit as st
import pandas as pd
import numpy as np
from modules.common_ui import render_sidebar_data_controls, render_page_header
from modules.data_loader import get_dataset_metadata
from modules.db_manager import save_checkpoint
from modules.data_cleaner import (
    clean_missing_values, remove_duplicates, cast_column_type,
    detect_and_handle_outliers, drop_selected_columns, rename_column, filter_dataset
)
from modules.feature_builder import (
    create_math_column, apply_transform, extract_date_features,
    create_binned_column, create_conditional_flag
)
from modules.bi_visualizer import build_bi_chart, build_executive_dashboard_charts, COLOR_THEMES
from modules.powerbi_excel_studio import (
    generate_pivot_table, compute_dax_measures, build_powerbi_matrix_chart
)

working_df = render_sidebar_data_controls()
render_page_header("📊 Data & BI Studio", working_df)

meta = get_dataset_metadata(working_df)

st.markdown("### 📊 Flagship Data & Business Intelligence Studio")
st.caption("Consolidated environment for in-browser data exploration, automated cleaning & feature engineering, executive BI dashboards, and dynamic pivot matrices.")

tab_explore, tab_clean, tab_bi, tab_pivot = st.tabs([
    "📋 Smart Spreadsheet & Explorer",
    "🧹 Data Cleaner & Feature Lab",
    "🖥️ Executive BI Dashboard",
    "🔲 Pivot & DAX Matrix Studio"
])

# ==============================================================
# TAB 1: SMART SPREADSHEET & EXPLORER
# ==============================================================
with tab_explore:
    st.markdown("##### 📋 Interactive Spreadsheet & Data Grid")
    st.caption("View, filter, sort, or edit cell records in real time. Changes can be committed directly to persistent project checkpoints.")

    # High-level dataset summary bar
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Total Rows", f"{meta.get('rows', 0):,}")
    m2.metric("Total Columns", f"{meta.get('cols', 0)}")
    m3.metric("Missing Cells", f"{meta.get('missing_cells', 0):,} ({meta.get('missing_pct', 0)}%)")
    m4.metric("Health Index", f"{meta.get('health_score', 100)}/100")

    # Editable Dataframe
    edited_df = st.data_editor(
        working_df,
        width="stretch",
        num_rows="dynamic",
        key="data_studio_editor"
    )

    if st.button("💾 Commit Grid Edits to Checkpoint", type="primary", key="btn_commit_grid_edits"):
        st.session_state.df = edited_df.copy()
        st.session_state.raw_df = edited_df.copy()
        save_checkpoint(st.session_state.project_id, "Spreadsheet Grid Edit", edited_df, "In-browser spreadsheet cell modifications")
        st.session_state.last_action_msg = "Successfully committed grid edits to project state!"
        st.rerun()

    with st.expander("🔍 Detailed Schema & Column Profiling", expanded=False):
        if "col_summary" in meta and isinstance(meta["col_summary"], pd.DataFrame):
            st.dataframe(meta["col_summary"], width="stretch", hide_index=True)


# ==============================================================
# TAB 2: DATA CLEANER & FEATURE LAB
# ==============================================================
with tab_clean:
    st.markdown("##### 🧹 Automated Data Cleaner & Feature Transformation Lab")
    st.caption("Perform missing value imputation, row deduplication, type casting, outlier clamping, and mathematical formula construction.")

    c_mode = st.radio(
        "Action Category",
        ["Missing Values", "Deduplication", "Outlier Sentinel", "Type Casting & Renaming", "Feature Builder"],
        horizontal=True,
        key="clean_mode_radio"
    )

    if c_mode == "Missing Values":
        null_cols = [c for c in working_df.columns if working_df[c].isnull().sum() > 0]
        if null_cols:
            cl1, cl2, cl3 = st.columns(3)
            with cl1:
                target_null_col = st.selectbox("Target Column with Missing Values", null_cols, key="cl_null_col")
            with cl2:
                is_num = pd.api.types.is_numeric_dtype(working_df[target_null_col])
                strategies = ["median", "mean", "mode", "constant", "drop_rows"] if is_num else ["mode", "constant", "drop_rows"]
                strategy = st.selectbox("Imputation Strategy", strategies, key="cl_null_strat")
            with cl3:
                fill_val = st.text_input("Fill Value (if constant)", value="Unknown", key="cl_null_const") if strategy == "constant" else None

            if st.button("⚡ Apply Imputation", type="primary", key="btn_apply_impute"):
                new_df, msg = clean_missing_values(working_df, target_null_col, strategy, fill_val)
                st.session_state.df = new_df.copy()
                save_checkpoint(st.session_state.project_id, "Data Cleaning: Imputation", new_df, msg)
                st.session_state.last_action_msg = msg
                st.rerun()
        else:
            st.success("🎉 No missing values detected in the active dataset!")

    elif c_mode == "Deduplication":
        dup_count = working_df.duplicated().sum()
        st.write(f"Identified **{dup_count:,} duplicate rows** in the current dataset.")
        if dup_count > 0:
            if st.button("🗑️ Remove All Duplicate Records", type="primary", key="btn_dedup"):
                new_df, msg = remove_duplicates(working_df)
                st.session_state.df = new_df.copy()
                save_checkpoint(st.session_state.project_id, "Data Cleaning: Deduplication", new_df, msg)
                st.session_state.last_action_msg = msg
                st.rerun()
        else:
            st.success("✅ Dataset has zero duplicate rows!")

    elif c_mode == "Outlier Sentinel":
        num_cols = meta.get("numeric_cols", [])
        if num_cols:
            o1, o2, o3 = st.columns(3)
            with o1:
                target_outlier_col = st.selectbox("Target Numerical Column", num_cols, key="outlier_col_sel")
            with o2:
                o_method = st.selectbox("Detection Method", ["zscore", "iqr"], key="outlier_method_sel")
            with o3:
                o_action = st.selectbox("Action", ["cap", "remove"], key="outlier_action_sel")

            if st.button("⚡ Handle Outliers", type="primary", key="btn_outliers"):
                new_df, msg, count = detect_and_handle_outliers(working_df, target_outlier_col, method=o_method, action=o_action)
                st.session_state.df = new_df.copy()
                save_checkpoint(st.session_state.project_id, "Data Cleaning: Outlier Clamping", new_df, msg)
                st.session_state.last_action_msg = msg
                st.rerun()
        else:
            st.info("No numerical columns available for outlier detection.")

    elif c_mode == "Type Casting & Renaming":
        ren1, ren2 = st.columns(2)
        with ren1:
            st.markdown("###### Rename Column")
            old_col = st.selectbox("Column to Rename", working_df.columns.tolist(), key="ren_old_col")
            new_name = st.text_input("New Name", value=old_col, key="ren_new_name")
            if st.button("Apply Rename", key="btn_apply_rename"):
                if new_name and new_name != old_col:
                    new_df, msg = rename_column(working_df, old_col, new_name)
                    st.session_state.df = new_df.copy()
                    save_checkpoint(st.session_state.project_id, "Schema Rename", new_df, msg)
                    st.session_state.last_action_msg = msg
                    st.rerun()

        with ren2:
            st.markdown("###### Cast Data Type")
            cast_col = st.selectbox("Target Column", working_df.columns.tolist(), key="cast_col")
            target_type = st.selectbox("Convert To", ["float", "int", "str", "datetime", "category"], key="cast_type")
            if st.button("Apply Conversion", key="btn_apply_cast"):
                new_df, msg = cast_column_type(working_df, cast_col, target_type)
                st.session_state.df = new_df.copy()
                save_checkpoint(st.session_state.project_id, "Type Casting", new_df, msg)
                st.session_state.last_action_msg = msg
                st.rerun()

    elif c_mode == "Feature Builder":
        st.markdown("###### Mathematical Feature Formula (Col A [op] Col B)")
        num_cols = meta.get("numeric_cols", [])
        if len(num_cols) >= 2:
            f1, f2, f3, f4 = st.columns(4)
            with f1:
                col_a = st.selectbox("Column A", num_cols, key="fb_col_a")
            with f2:
                op = st.selectbox("Operator", ["add", "subtract", "multiply", "divide"], key="fb_op")
            with f3:
                col_b = st.selectbox("Column B", num_cols, key="fb_col_b")
            with f4:
                out_name = st.text_input("New Column Name", value=f"{col_a}_{op}_{col_b}", key="fb_out_name")

            if st.button("⚡ Construct Math Feature", type="primary", key="btn_apply_math_feat"):
                new_df, msg = create_math_column(working_df, col_a, col_b, op, out_name)
                st.session_state.df = new_df.copy()
                save_checkpoint(st.session_state.project_id, "Feature Engineering", new_df, msg)
                st.session_state.last_action_msg = msg
                st.rerun()


# ==============================================================
# TAB 3: EXECUTIVE BI DASHBOARD
# ==============================================================
with tab_bi:
    st.markdown("##### 🖥️ Executive Business Intelligence Dashboard")
    st.caption("Interactive cross-visual dashboards, KPIs, and Custom Visual Builder matching Power BI & Tableau.")

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
    bi_r1, bi_r2 = st.columns(2)
    with bi_r1:
        if "cat_bar" in exec_charts:
            st.plotly_chart(exec_charts["cat_bar"], width="stretch", key="dstudio_cat_bar_plot")
    with bi_r2:
        if "trend" in exec_charts:
            st.plotly_chart(exec_charts["trend"], width="stretch", key="dstudio_trend_plot")

    bi_r3, bi_r4 = st.columns(2)
    with bi_r3:
        if "donut" in exec_charts:
            st.plotly_chart(exec_charts["donut"], width="stretch", key="dstudio_donut_plot")
    with bi_r4:
        if "scatter" in exec_charts:
            st.plotly_chart(exec_charts["scatter"], width="stretch", key="dstudio_scatter_plot")

    st.markdown("---")
    with st.expander("🎨 Custom Visual Builder Studio", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            custom_chart_type = st.selectbox(
                "Chart Type",
                ["Bar Chart", "Line Chart", "Area Chart", "Scatter / Bubble Plot", "Pie / Donut Chart", "Box Plot", "Histogram", "Treemap"],
                key="ds_custom_chart_type"
            )
        with c2:
            custom_x = st.selectbox("X-Axis Dimension", working_df.columns.tolist(), key="ds_custom_x")
        with c3:
            num_opts = ["None"] + meta.get("numeric_cols", [])
            custom_y = st.selectbox("Y-Axis Metric", num_opts, index=1 if len(num_opts) > 1 else 0, key="ds_custom_y")
            actual_y = None if custom_y == "None" else custom_y
        with c4:
            custom_agg = st.selectbox("Aggregation", ["Sum", "Average", "Count", "Median", "Min", "Max"], key="ds_custom_agg")

        custom_fig = build_bi_chart(
            df=working_df,
            chart_type=custom_chart_type,
            x_col=custom_x,
            y_col=actual_y,
            color_col="None",
            size_col="None",
            aggregation=custom_agg,
            theme_name="Neon Cyberpunk",
            title=f"{custom_chart_type}: {custom_x}"
        )
        if custom_fig:
            st.plotly_chart(custom_fig, width="stretch", key="ds_custom_plot")


# ==============================================================
# TAB 4: PIVOT & DAX MATRIX STUDIO
# ==============================================================
with tab_pivot:
    st.markdown("##### 🔲 Multi-Dimensional Pivot Matrix & Power BI DAX Measures")
    st.caption("Compute dynamic pivot tables with row hierarchies and calculate equivalent Power BI DAX measures.")

    pvi_t1, pvi_t2 = st.tabs(["🔲 Dynamic Multi-Level Pivot", "📐 Power BI DAX Measures"])

    with pvi_t1:
        num_choices = meta.get("numeric_cols", [])
        all_cols = working_df.columns.tolist()

        pv_c1, pv_c2, pv_c3, pv_c4 = st.columns(4)
        with pv_c3:
            val_col = st.selectbox("Aggregated Metric", num_choices if num_choices else all_cols, key="ds_pivot_val")

        dim_candidates = [c for c in all_cols if c != val_col]
        with pv_c1:
            row_dims = st.multiselect("Row Dimensions", dim_candidates, default=[dim_candidates[0]] if dim_candidates else [], key="ds_pivot_rows")
        with pv_c2:
            rem_dims = [c for c in dim_candidates if c not in row_dims]
            col_dims = st.multiselect("Column Dimension", rem_dims, default=[rem_dims[0]] if rem_dims else [], key="ds_pivot_cols")
        with pv_c4:
            agg_method = st.selectbox("Calculation", ["Sum", "Average", "Count", "Min", "Max"], key="ds_pivot_agg")

        if row_dims and val_col:
            try:
                pivot_res = generate_pivot_table(working_df, row_dims, col_dims, val_col, agg_func=agg_method, add_margins=True)
                if not pivot_res.empty:
                    st.dataframe(pivot_res, width="stretch", key="ds_pivot_matrix_view")
                    st.download_button("📥 Download Pivot Matrix (.csv)", data=pivot_res.to_csv().encode("utf-8"), file_name="Pivot_Matrix.csv", mime="text/csv", key="ds_dl_pivot_btn")
            except Exception as e:
                st.warning(f"Could not compute pivot: {e}")

    with pvi_t2:
        if num_choices and all_cols:
            dx1, dx2, dx3 = st.columns(3)
            with dx1:
                dax_dim = st.selectbox("Target Dimension", all_cols, key="ds_dax_dim")
            with dx2:
                dax_metric = st.selectbox("Base Metric", num_choices, key="ds_dax_metric")
            with dx3:
                dax_type = st.selectbox("DAX Formula Pattern", ["contribution_pct", "running_total", "moving_avg", "growth_rate"], key="ds_dax_type")

            try:
                dax_df, dax_formula = compute_dax_measures(working_df, dax_dim, dax_metric, dax_type)
                st.info(f"💡 **Equivalent DAX Formula:** `{dax_formula}`")
                matrix_fig = build_powerbi_matrix_chart(dax_df, dax_dim, dax_metric, dax_df.columns[-1])
                st.plotly_chart(matrix_fig, width="stretch", key="ds_dax_matrix_chart")
                st.dataframe(dax_df, width="stretch", key="ds_dax_table")
            except Exception as e:
                st.warning(f"DAX measure calculation: {e}")
