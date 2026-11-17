import streamlit as st
import pandas as pd
from modules.common_ui import render_sidebar_data_controls, render_page_header
from modules.data_cleaner import (
    clean_missing_values, remove_duplicates, cast_column_type,
    detect_and_handle_outliers, drop_selected_columns, rename_column
)
from modules.feature_builder import (
    create_math_column, apply_transform, extract_date_features,
    create_binned_column
)
from modules.data_loader import get_dataset_metadata
from modules.db_manager import save_checkpoint

working_df = render_sidebar_data_controls()
render_page_header("🧹 Data Cleaning & Feature Studio", working_df)

meta = get_dataset_metadata(working_df)

st.markdown("### 🧹 Data Cleaning, Imputation & Feature Engineering Studio")
st.caption("Fix missing data, purge duplicates, convert data types, clamp outliers, and build calculated formula columns.")

dc_tab1, dc_tab2 = st.tabs(["🧹 Data Cleanser & Outliers", "⚡ Feature & Formula Builder"])

with dc_tab1:
    clean_accordion = st.tabs([
        "🩹 Missing Values",
        "👥 Deduplication",
        "🏷️ Type Casting",
        "🎯 Outlier Treatment",
        "✂️ Manage Columns"
    ])

    with clean_accordion[0]:
        st.markdown("##### Handle Missing Cells")
        target_missing_col = st.selectbox("Column to Impute", ["All Columns"] + working_df.columns.tolist(), help="Choose which column to fill nulls in.")
        impute_strategy = st.selectbox(
            "Imputation Method",
            ["mean", "median", "mode", "zero", "custom", "ffill", "bfill", "drop_rows", "drop_col"],
            help="Mean/Median for numbers, Mode for categories, Zero, or Custom text."
        )
        custom_input = None
        if impute_strategy == "custom":
            custom_input = st.text_input("Custom Impute String/Value", "Unknown")

        if st.button("Apply Imputation", type="primary"):
            cleaned_res, msg = clean_missing_values(st.session_state.df, target_missing_col, impute_strategy, custom_input)
            st.session_state.df = cleaned_res
            st.session_state.audit_log.append(f"Imputed '{target_missing_col}' via {impute_strategy}.")
            st.session_state.current_stage = f"Cleaned: {impute_strategy} on {target_missing_col}"
            save_checkpoint(st.session_state.project_id, st.session_state.current_stage, cleaned_res, msg)
            st.session_state.last_action_msg = msg
            st.rerun()

    with clean_accordion[1]:
        st.markdown("##### Detect & Eliminate Duplicate Records")
        dup_cnt = meta.get("duplicates", 0)
        st.info(f"Duplicate row count detected: **{dup_cnt}** ({meta.get('duplicate_pct', 0)}% of dataset)")
        dedup_subset = st.multiselect("Subset of Columns for Uniqueness (Optional)", working_df.columns.tolist())
        keep_rule = st.radio("Keep Strategy", ["first", "last"], horizontal=True)

        if st.button("Purge Duplicate Rows", type="primary"):
            cleaned_res, msg = remove_duplicates(st.session_state.df, subset_cols=dedup_subset, keep=keep_rule)
            st.session_state.df = cleaned_res
            st.session_state.audit_log.append(msg)
            st.session_state.current_stage = "Cleaned: Deduplication"
            save_checkpoint(st.session_state.project_id, st.session_state.current_stage, cleaned_res, msg)
            st.session_state.last_action_msg = msg
            st.rerun()

    with clean_accordion[2]:
        st.markdown("##### Convert Column Data Types")
        tc1, tc2 = st.columns(2)
        with tc1:
            col_to_convert = st.selectbox("Select Target Column", working_df.columns.tolist())
        with tc2:
            new_dtype = st.selectbox("Desired Data Type", ["float", "int", "str", "datetime", "category", "bool"])

        if st.button("Convert Column Type", type="primary"):
            cleaned_res, msg = cast_column_type(st.session_state.df, col_to_convert, new_dtype)
            st.session_state.df = cleaned_res
            st.session_state.audit_log.append(msg)
            st.session_state.current_stage = f"Casted {col_to_convert} to {new_dtype}"
            save_checkpoint(st.session_state.project_id, st.session_state.current_stage, cleaned_res, msg)
            st.session_state.last_action_msg = msg
            st.rerun()

    with clean_accordion[3]:
        st.markdown("##### Statistical Outlier Detection & Clamping")
        num_candidates = meta.get("numeric_cols", [])
        if num_candidates:
            outlier_field = st.selectbox("Select Numeric Field", num_candidates)
            oc1, oc2 = st.columns(2)
            with oc1:
                detect_method = st.radio("Method", ["iqr", "zscore"], format_func=lambda x: "IQR (1.5x Interquartile)" if x == "iqr" else "Z-Score (|z| > 3)", horizontal=True, help="IQR is robust for business data; Z-score is standard for bell-curve data.")
            with oc2:
                outlier_action = st.radio("Action", ["clamp", "drop"], format_func=lambda x: "Clamp to Thresholds (Winsorize)" if x == "clamp" else "Drop Outlier Rows", horizontal=True, help="Clamp pulls extreme freak values to the boundary rather than deleting rows.")

            if st.button("Process Outliers", type="primary"):
                cleaned_res, msg, cnt = detect_and_handle_outliers(st.session_state.df, outlier_field, method=detect_method, action=outlier_action)
                st.session_state.df = cleaned_res
                st.session_state.audit_log.append(msg)
                st.session_state.current_stage = f"Outliers: {outlier_action} on {outlier_field}"
                save_checkpoint(st.session_state.project_id, st.session_state.current_stage, cleaned_res, msg)
                st.session_state.last_action_msg = msg
                st.rerun()
        else:
            st.warning("No numeric columns found for outlier processing.")

    with clean_accordion[4]:
        st.markdown("##### Column Management")
        mc1, mc2 = st.columns(2)
        with mc1:
            cols_to_del = st.multiselect("Drop Columns", working_df.columns.tolist())
            if st.button("Drop Selected Columns", type="primary"):
                if cols_to_del:
                    cleaned_res, msg = drop_selected_columns(st.session_state.df, cols_to_del)
                    st.session_state.df = cleaned_res
                    st.session_state.audit_log.append(msg)
                    st.session_state.current_stage = f"Dropped {len(cols_to_del)} columns"
                    save_checkpoint(st.session_state.project_id, st.session_state.current_stage, cleaned_res, msg)
                    st.session_state.last_action_msg = msg
                    st.rerun()

        with mc2:
            rename_target = st.selectbox("Rename Column", working_df.columns.tolist())
            new_title = st.text_input("New Column Name", "")
            if st.button("Save New Name", type="primary"):
                if new_title:
                    cleaned_res, msg = rename_column(st.session_state.df, rename_target, new_title)
                    st.session_state.df = cleaned_res
                    st.session_state.audit_log.append(msg)
                    st.session_state.current_stage = f"Renamed {rename_target} to {new_title}"
                    save_checkpoint(st.session_state.project_id, st.session_state.current_stage, cleaned_res, msg)
                    st.session_state.last_action_msg = msg
                    st.rerun()

with dc_tab2:
    feat_tabs = st.tabs(["🧮 Math Formulas", "📐 Transforms", "📅 Dates", "📊 Bins"])
    with feat_tabs[0]:
        st.markdown("##### Construct Calculated Formula Column")
        num_cols = meta.get("numeric_cols", [])
        if num_cols:
            formula_name = st.text_input("New Column Name", "Calculated_Metric")
            fc1, fc2, fc3, fc4 = st.columns(4)
            with fc1:
                col_a = st.selectbox("Column A", num_cols, key="feat_col_a")
            with fc2:
                operator = st.selectbox("Operator", ["+", "-", "*", "/", "%", "power"])
            with fc3:
                use_const = st.checkbox("Use Constant Value", value=False)
            with fc4:
                if use_const:
                    col_b_or_const = st.number_input("Constant", value=1.0)
                else:
                    col_b_or_const = st.selectbox("Column B", num_cols, key="feat_col_b")

            if st.button("Generate Formula Column", type="primary"):
                res_df, msg = create_math_column(st.session_state.df, formula_name, col_a, operator, col_b_or_const, is_scalar=use_const)
                st.session_state.df = res_df
                st.session_state.audit_log.append(msg)
                st.session_state.current_stage = f"Feature Added: {formula_name}"
                save_checkpoint(st.session_state.project_id, st.session_state.current_stage, res_df, msg)
                st.session_state.last_action_msg = msg
                st.rerun()
        else:
            st.warning("Numeric columns required to create mathematical formulas.")

    with feat_tabs[1]:
        st.markdown("##### Single-Column Transforms")
        num_cols = meta.get("numeric_cols", [])
        if num_cols:
            tr1, tr2, tr3 = st.columns(3)
            with tr1:
                trans_target = st.selectbox("Target Field", num_cols, key="trans_target")
            with tr2:
                trans_func = st.selectbox("Transform Function", ["log", "log1p", "sqrt", "abs", "square", "round"], help="Log transforms help normalize skewed positive numbers.")
            with tr3:
                trans_out_name = st.text_input("Output Column Name", f"{trans_target}_{trans_func}")

            if st.button("Apply Transform", type="primary"):
                res_df, msg = apply_transform(st.session_state.df, trans_out_name, trans_target, trans_func)
                st.session_state.df = res_df
                st.session_state.audit_log.append(msg)
                st.session_state.current_stage = f"Transform: {trans_out_name}"
                save_checkpoint(st.session_state.project_id, st.session_state.current_stage, res_df, msg)
                st.session_state.last_action_msg = msg
                st.rerun()

    with feat_tabs[2]:
        st.markdown("##### Extract Date Components")
        candidate_dates = [c for c in working_df.columns if "date" in c.lower() or "time" in c.lower() or pd.api.types.is_datetime64_any_dtype(working_df[c])]
        if not candidate_dates:
            candidate_dates = working_df.columns.tolist()

        date_field = st.selectbox("Date / Timestamp Column", candidate_dates)
        components = st.multiselect(
            "Select Components to Extract",
            ["Year", "Month", "Month Name", "Quarter", "Day of Week", "Day of Month", "Is Weekend"],
            default=["Year", "Month Name", "Day of Week"],
            help="Breaks dates down into quarters, day of week, or month names for time-series charts."
        )
        if st.button("Extract Date Features", type="primary"):
            res_df, msg = extract_date_features(st.session_state.df, date_field, components)
            st.session_state.df = res_df
            st.session_state.audit_log.append(msg)
            st.session_state.current_stage = f"Date Intelligence on {date_field}"
            save_checkpoint(st.session_state.project_id, st.session_state.current_stage, res_df, msg)
            st.session_state.last_action_msg = msg
            st.rerun()

    with feat_tabs[3]:
        st.markdown("##### Discretize Numbers into Quantile Bins")
        num_cols = meta.get("numeric_cols", [])
        if num_cols:
            bin_target = st.selectbox("Numeric Column to Discretize", num_cols, key="bin_target_select")
            bc1, bc2 = st.columns(2)
            with bc1:
                bin_count = st.slider("Quantile Groups (Bins)", 2, 6, 3, help="e.g. 3 bins creates Low, Medium, and High tiers.")
            with bc2:
                bin_out_name = st.text_input("Binned Name", f"{bin_target}_Tier")

            if st.button("Create Quantile Bins", type="primary"):
                res_df, msg = create_binned_column(st.session_state.df, bin_out_name, bin_target, n_bins=bin_count)
                st.session_state.df = res_df
                st.session_state.audit_log.append(msg)
                st.session_state.current_stage = f"Binned: {bin_out_name}"
                save_checkpoint(st.session_state.project_id, st.session_state.current_stage, res_df, msg)
                st.session_state.last_action_msg = msg
                st.rerun()

