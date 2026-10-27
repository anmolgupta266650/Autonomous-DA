import os
import streamlit as st
import pandas as pd
import numpy as np

# Page configuration
st.set_page_config(
    page_title="Autonomous DA | No-Code Analytics & BI Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom Modules
from modules.data_loader import (
    load_file, get_excel_sheet_names, get_dataset_metadata,
    get_available_real_datasets, load_real_dataset
)
from modules.data_cleaner import (
    clean_missing_values, remove_duplicates, cast_column_type,
    detect_and_handle_outliers, drop_selected_columns, rename_column
)
from modules.feature_builder import (
    create_math_column, apply_transform, extract_date_features,
    create_binned_column
)
from modules.eda_profiler import (
    get_detailed_statistics, plot_missing_values,
    plot_correlation_heatmap, plot_feature_distribution
)
from modules.bi_visualizer import (
    build_bi_chart, build_executive_dashboard_charts, COLOR_THEMES
)
from modules.business_insights import generate_executive_insights
from modules.automl_engine import (
    detect_task_type, prepare_ml_data, train_and_evaluate_models
)
from modules.report_exporter import (
    export_to_csv, export_to_excel, generate_executive_html_report
)


# Inject custom styling
def load_custom_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

load_custom_css()


# ==========================================
# SESSION STATE INITIALIZATION
# ==========================================
if "raw_df" not in st.session_state:
    st.session_state.raw_df = None
if "df" not in st.session_state:
    st.session_state.df = None
if "audit_log" not in st.session_state:
    st.session_state.audit_log = []
if "dataset_name" not in st.session_state:
    st.session_state.dataset_name = "Global Superstore Sales (1,200 Real Transactions)"
if "trained_ml" not in st.session_state:
    st.session_state.trained_ml = None
if "last_action_msg" not in st.session_state:
    st.session_state.last_action_msg = None

# Default load real dataset
if st.session_state.df is None:
    real_data = load_real_dataset("🛒 Global Superstore Sales (1,200 transactions)")
    st.session_state.raw_df = real_data.copy()
    st.session_state.df = real_data.copy()
    st.session_state.audit_log.append("Initialized authentic Global Superstore 2024 commercial dataset.")


# ==========================================
# SIDEBAR: DATA CONNECTOR & CONTROLS
# ==========================================
with st.sidebar:
    st.markdown("### ⚡ Autonomous DA")
    st.caption("Enterprise No-Code Analytics & BI Suite")
    st.markdown("---")

    ingestion_mode = st.radio(
        "📁 Data Source Mode",
        ["Real Benchmark Datasets", "Upload Custom File"],
        index=0
    )

    if ingestion_mode == "Real Benchmark Datasets":
        real_datasets = get_available_real_datasets()
        selected_real = st.selectbox(
            "Select Real-World Dataset",
            list(real_datasets.keys()),
            index=0
        )
        if st.button("📥 Load Dataset", type="primary"):
            loaded_df = load_real_dataset(selected_real)
            st.session_state.raw_df = loaded_df.copy()
            st.session_state.df = loaded_df.copy()
            st.session_state.dataset_name = selected_real
            st.session_state.audit_log = [f"Loaded dataset: {selected_real}"]
            st.session_state.trained_ml = None
            st.session_state.last_action_msg = f"Successfully loaded {selected_real}!"
            st.rerun()

    else:
        uploaded_file = st.file_uploader(
            "Upload CSV, Excel, or JSON",
            type=["csv", "xlsx", "xls", "json"]
        )
        if uploaded_file is not None:
            sheet_choice = None
            if uploaded_file.name.lower().endswith((".xlsx", ".xls")):
                sheets = get_excel_sheet_names(uploaded_file)
                if len(sheets) > 1:
                    sheet_choice = st.selectbox("Select Excel Sheet", sheets)

            if st.button("⚡ Ingest Uploaded File", type="primary"):
                df_loaded, err = load_file(uploaded_file, sheet_name=sheet_choice)
                if err:
                    st.error(err)
                else:
                    st.session_state.raw_df = df_loaded.copy()
                    st.session_state.df = df_loaded.copy()
                    st.session_state.dataset_name = uploaded_file.name
                    st.session_state.audit_log = [f"Uploaded custom file: {uploaded_file.name}"]
                    st.session_state.trained_ml = None
                    st.session_state.last_action_msg = f"Uploaded and ingested {uploaded_file.name} successfully!"
                    st.rerun()

    st.markdown("---")
    
    # Global Interactive Slicer
    st.markdown("#### 🎯 Global Interactive Slicer")
    cat_columns = st.session_state.df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
    filter_cat = None
    selected_category_val = "All"
    if cat_columns:
        filter_cat = st.selectbox("Filter Dimension", ["None"] + cat_columns)
        if filter_cat != "None":
            unique_vals = ["All"] + sorted(st.session_state.df[filter_cat].dropna().unique().tolist())[:30]
            selected_category_val = st.selectbox(f"Select {filter_cat}", unique_vals)

    st.markdown("---")
    st.markdown("#### 🔄 Dataset Actions")
    if st.button("↺ Reset Dataset to Original"):
        if st.session_state.raw_df is not None:
            st.session_state.df = st.session_state.raw_df.copy()
            st.session_state.audit_log.append("Reset dataset to original imported state.")
            st.session_state.trained_ml = None
            st.session_state.last_action_msg = "Dataset restored to original raw state."
            st.rerun()

    st.markdown("---")
    st.markdown("#### 📋 Action Audit Trail")
    if st.session_state.audit_log:
        for entry in reversed(st.session_state.audit_log[-4:]):
            st.caption(f"• {entry}")


# Apply Global Slicer if active
working_df = st.session_state.df.copy()
if filter_cat and filter_cat != "None" and selected_category_val != "All":
    working_df = working_df[working_df[filter_cat] == selected_category_val].reset_index(drop=True)

meta = get_dataset_metadata(working_df)


# ==========================================
# MODERN SAAS HEADER NAVBAR
# ==========================================
st.markdown(f"""
<div class="nexus-navbar">
    <div>
        <h1 class="brand-title">⚡ Autonomous DA</h1>
        <p class="brand-tagline">Intelligent No-Code Data Analytics, Wrangling & Business Intelligence Platform</p>
    </div>
    <div class="nav-badges">
        <span class="nav-pill">
            <span class="dot-indicator dot-green"></span> Source: <strong>{st.session_state.dataset_name}</strong>
        </span>
        <span class="nav-pill">
            <span class="dot-indicator dot-cyan"></span> Active Records: <strong>{meta.get('rows', 0):,}</strong>
        </span>
        <span class="nav-pill">
            <span class="dot-indicator dot-purple"></span> Health Score: <strong>{meta.get('health_score', 100)}/100</strong>
        </span>
    </div>
</div>
""", unsafe_allow_html=True)

if st.session_state.last_action_msg:
    st.success(f"✅ {st.session_state.last_action_msg}")
    st.session_state.last_action_msg = None


# ==========================================
# MAIN APPLICATION TABS
# ==========================================
tab_dashboard, tab_spreadsheet, tab_cleanser, tab_features, tab_eda, tab_insights, tab_automl, tab_export = st.tabs([
    "🖥️ Executive BI Dashboard",
    "📊 Smart Spreadsheet",
    "🧹 Data Cleanser & Wrangler",
    "⚡ Feature & Formula Builder",
    "🔍 Automated EDA Profiler",
    "💡 AI Business Insights",
    "🤖 Predictive Analytics & AutoML",
    "📥 Export & Reports"
])


# ----------------------------------------------------
# TAB 1: EXECUTIVE BI DASHBOARD (POWER BI / TABLEAU)
# ----------------------------------------------------
with tab_dashboard:
    st.markdown("### 🖥️ Executive Business Intelligence Dashboard")
    st.caption("Dynamic, multi-visual analytics dashboard matching Power BI and Tableau capabilities.")

    # Top Metric Tiles
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

    # 4-Chart Executive Grid Layout
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
    
    # Custom Chart Visual Studio
    with st.expander("🎨 Custom Visual Builder (Design Any Custom Chart)", expanded=False):
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            custom_chart_type = st.selectbox(
                "Chart Type",
                ["Bar Chart", "Line Chart", "Area Chart", "Scatter / Bubble Plot", "Pie / Donut Chart", "Box Plot", "Violin Plot", "Histogram", "Treemap", "Sunburst"],
                key="custom_chart_type"
            )
        with c2:
            custom_x = st.selectbox("X-Axis Dimension", working_df.columns.tolist(), key="custom_x")
        with c3:
            num_opts = ["None"] + meta.get("numeric_cols", [])
            custom_y = st.selectbox("Y-Axis Metric", num_opts, index=1 if len(num_opts) > 1 else 0, key="custom_y")
            actual_y = None if custom_y == "None" else custom_y
        with c4:
            custom_agg = st.selectbox("Aggregation", ["Sum", "Average", "Count", "Median", "Min", "Max", "Std Dev"], key="custom_agg")

        c5, c6, c7, c8 = st.columns(4)
        with c5:
            custom_color = st.selectbox("Legend / Hue", ["None"] + working_df.columns.tolist(), key="custom_color")
        with c6:
            custom_size = st.selectbox("Bubble Size (Scatter)", ["None"] + meta.get("numeric_cols", []), key="custom_size")
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


# ----------------------------------------------------
# TAB 2: SMART SPREADSHEET & DATA HUB
# ----------------------------------------------------
with tab_spreadsheet:
    st.markdown("### 📊 Interactive Smart Spreadsheet & Data Hub")
    st.caption("Live spreadsheet grid with instant keyword search, sorting, and structural schema breakdown.")

    sc1, sc2 = st.columns([3, 1])
    with sc1:
        search_kw = st.text_input("🔍 Quick Keyword Filter", placeholder="Search any term...")
    with sc2:
        page_size = st.selectbox("Display Limit", [20, 50, 100, "All Records"], index=0)

    grid_df = working_df
    if search_kw:
        mask = working_df.astype(str).apply(lambda row: row.str.contains(search_kw, case=False).any(), axis=1)
        grid_df = working_df[mask]

    if page_size != "All Records":
        grid_df = grid_df.head(int(page_size))

    st.dataframe(grid_df, width="stretch", height=420)

    st.markdown("#### 📋 Column Schema & Health Breakdown")
    st.dataframe(meta.get("col_summary", pd.DataFrame()), width="stretch")


# ----------------------------------------------------
# TAB 3: DATA CLEANSER & WRANGLER
# ----------------------------------------------------
with tab_cleanser:
    st.markdown("### 🧹 Excel-Style Data Cleanser & Transformation Studio")
    st.caption("Resolve missing cells, purge duplicate records, cast column datatypes, and clamp statistical outliers.")

    clean_accordion = st.tabs([
        "🩹 Missing Value Imputation",
        "👥 Deduplication",
        "🏷️ Type Casting",
        "🎯 Outlier Treatment (IQR / Z-Score)",
        "✂️ Manage & Rename Columns"
    ])

    # 1. Missing Values
    with clean_accordion[0]:
        st.markdown("##### Handle Missing Cells")
        target_missing_col = st.selectbox("Column to Impute", ["All Columns"] + working_df.columns.tolist())
        impute_strategy = st.selectbox(
            "Imputation Method",
            ["mean", "median", "mode", "zero", "custom", "ffill", "bfill", "drop_rows", "drop_col"]
        )
        custom_input = None
        if impute_strategy == "custom":
            custom_input = st.text_input("Custom Impute String/Value", "Unknown")

        if st.button("Apply Imputation", type="primary"):
            cleaned_res, msg = clean_missing_values(st.session_state.df, target_missing_col, impute_strategy, custom_input)
            st.session_state.df = cleaned_res
            st.session_state.audit_log.append(f"Imputed '{target_missing_col}' via {impute_strategy}.")
            st.session_state.last_action_msg = msg
            st.rerun()

    # 2. Deduplication
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
            st.session_state.last_action_msg = msg
            st.rerun()

    # 3. Type Casting
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
            st.session_state.last_action_msg = msg
            st.rerun()

    # 4. Outlier Treatment
    with clean_accordion[3]:
        st.markdown("##### Statistical Outlier Detection & Clamping")
        num_candidates = meta.get("numeric_cols", [])
        if num_candidates:
            outlier_field = st.selectbox("Select Numeric Field", num_candidates)
            oc1, oc2 = st.columns(2)
            with oc1:
                detect_method = st.radio("Method", ["iqr", "zscore"], format_func=lambda x: "IQR (1.5x Interquartile)" if x == "iqr" else "Z-Score (|z| > 3)", horizontal=True)
            with oc2:
                outlier_action = st.radio("Action", ["clamp", "drop"], format_func=lambda x: "Clamp to Thresholds (Winsorize)" if x == "clamp" else "Drop Outlier Rows", horizontal=True)

            if st.button("Process Outliers", type="primary"):
                cleaned_res, msg, cnt = detect_and_handle_outliers(st.session_state.df, outlier_field, method=detect_method, action=outlier_action)
                st.session_state.df = cleaned_res
                st.session_state.audit_log.append(msg)
                st.session_state.last_action_msg = msg
                st.rerun()
        else:
            st.warning("No numeric columns found for outlier processing.")

    # 5. Manage Columns
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
                    st.session_state.last_action_msg = msg
                    st.rerun()


# ----------------------------------------------------
# TAB 4: FEATURE & FORMULA BUILDER
# ----------------------------------------------------
with tab_features:
    st.markdown("### ⚡ Feature Engineering & Formula Builder")
    st.caption("Construct calculated metrics, apply mathematical transforms, extract dates, and discretize into bins.")

    feat_tabs = st.tabs(["🧮 Math Formulas", "📐 Mathematical Transforms", "📅 Date Intelligence", "📊 Quantile Binning"])

    with feat_tabs[0]:
        st.markdown("##### Construct Calculated Formula Column")
        num_cols = meta.get("numeric_cols", [])
        if num_cols:
            formula_name = st.text_input("New Calculated Column Name", "Margin_Percentage")
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
                trans_func = st.selectbox("Transform Function", ["log", "log1p", "sqrt", "abs", "square", "round"])
            with tr3:
                trans_out_name = st.text_input("Output Column Name", f"{trans_target}_{trans_func}")

            if st.button("Apply Transform", type="primary"):
                res_df, msg = apply_transform(st.session_state.df, trans_out_name, trans_target, trans_func)
                st.session_state.df = res_df
                st.session_state.audit_log.append(msg)
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
            default=["Year", "Month Name", "Day of Week"]
        )
        if st.button("Extract Date Features", type="primary"):
            res_df, msg = extract_date_features(st.session_state.df, date_field, components)
            st.session_state.df = res_df
            st.session_state.audit_log.append(msg)
            st.session_state.last_action_msg = msg
            st.rerun()

    with feat_tabs[3]:
        st.markdown("##### Discretize Numbers into Quantile Bins")
        num_cols = meta.get("numeric_cols", [])
        if num_cols:
            bin_target = st.selectbox("Numeric Column to Discretize", num_cols, key="bin_target_select")
            bc1, bc2 = st.columns(2)
            with bc1:
                bin_count = st.slider("Quantile Groups (Bins)", 2, 6, 3)
            with bc2:
                bin_out_name = st.text_input("Binned Name", f"{bin_target}_Tier")

            if st.button("Create Quantile Bins", type="primary"):
                res_df, msg = create_binned_column(st.session_state.df, bin_out_name, bin_target, n_bins=bin_count)
                st.session_state.df = res_df
                st.session_state.audit_log.append(msg)
                st.session_state.last_action_msg = msg
                st.rerun()


# ----------------------------------------------------
# TAB 5: AUTOMATED EDA PROFILER
# ----------------------------------------------------
with tab_eda:
    st.markdown("### 🔍 Automated Exploratory Data Analysis (EDA)")
    st.caption("Deep statistical profiling, correlation matrices, and distribution breakdowns.")

    eda_tabs = st.tabs(["📊 Descriptive Statistics", "🔗 Correlation Heatmap", "🔬 Individual Feature Profiles"])

    with eda_tabs[0]:
        st.markdown("##### Extended Statistical Profile")
        stats_data = get_detailed_statistics(working_df)
        if not stats_data.empty:
            st.dataframe(stats_data, width="stretch")
        else:
            st.info("No numeric columns available for statistical profiling.")

        missing_fig = plot_missing_values(working_df)
        if missing_fig:
            st.plotly_chart(missing_fig, width="stretch")
        else:
            st.success("✅ Zero missing records detected across all features!")

    with eda_tabs[1]:
        st.markdown("##### Inter-Feature Correlation Heatmap")
        corr_fig, ranked_pairs = plot_correlation_heatmap(working_df)
        if corr_fig:
            st.plotly_chart(corr_fig, width="stretch")
            if not ranked_pairs.empty:
                st.markdown("###### Top Ranked Co-dependencies")
                st.dataframe(ranked_pairs.head(10), width="stretch")
        else:
            st.info("Requires at least 2 numeric features to calculate correlations.")

    with eda_tabs[2]:
        st.markdown("##### Single Feature Distribution")
        inspect_feat = st.selectbox("Inspect Feature", working_df.columns.tolist())
        feat_dist_fig = plot_feature_distribution(working_df, inspect_feat)
        if feat_dist_fig:
            st.plotly_chart(feat_dist_fig, width="stretch")


# ----------------------------------------------------
# TAB 6: AI BUSINESS INSIGHTS
# ----------------------------------------------------
with tab_insights:
    st.markdown("### 💡 AI Business Insights & Executive Advisor")
    st.caption("Automated pattern extraction, Pareto 80/20 driver analysis, and strategic recommendations.")

    insights_list = generate_executive_insights(working_df)

    if insights_list:
        for ins in insights_list:
            if ins["type"] == "success":
                st.markdown(f"""
                <div class="alert-insight">
                    <strong>✅ {ins['title']}</strong> [{ins['category']}]<br>
                    {ins['description']}
                </div>
                """, unsafe_allow_html=True)
            elif ins["type"] == "warning":
                st.markdown(f"""
                <div class="alert-warning">
                    <strong>⚠️ {ins['title']}</strong> [{ins['category']}]<br>
                    {ins['description']}
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown(f"""
                <div class="alert-ai">
                    <strong>💡 {ins['title']}</strong> [{ins['category']}]<br>
                    {ins['description']}
                </div>
                """, unsafe_allow_html=True)
    else:
        st.info("No specific business insights detected for the current dataset subset.")


# ----------------------------------------------------
# TAB 7: PREDICTIVE ANALYTICS & AUTOML
# ----------------------------------------------------
with tab_automl:
    st.markdown("### 🤖 Predictive Analytics & AutoML Studio")
    st.caption("Benchmark classification and regression algorithms, inspect feature importances, and run What-If simulations.")

    ml_col1, ml_col2 = st.columns([1, 2])

    with ml_col1:
        st.markdown("##### ⚙️ Model Setup")
        target_choice = st.selectbox("Target Variable to Predict", working_df.columns.tolist())
        inferred_task = detect_task_type(working_df[target_choice])
        st.info(f"Task Auto-Detected: **{inferred_task.upper()}**")

        selectable_features = [c for c in working_df.columns if c != target_choice]
        filtered_default_feats = [c for c in selectable_features if not c.lower().endswith("id")]
        chosen_features = st.multiselect("Predictor Features", selectable_features, default=filtered_default_feats)

        train_trigger = st.button("🚀 Train & Benchmark Models", type="primary")

    with ml_col2:
        if train_trigger:
            if not chosen_features:
                st.error("Please pick at least one feature.")
            else:
                with st.spinner("Training and benchmarking models..."):
                    try:
                        X, y, task_t, t_enc, f_encs = prepare_ml_data(working_df, target_choice, chosen_features)
                        results_df, models_dict, best_m, diag_plot, feat_plot, test_data = train_and_evaluate_models(X, y, task_t)
                        
                        st.session_state.trained_ml = {
                            "results_df": results_df,
                            "models_dict": models_dict,
                            "best_model_name": best_m,
                            "diag_plot": diag_plot,
                            "feat_plot": feat_plot,
                            "task_type": task_t,
                            "target_col": target_choice,
                            "features": chosen_features,
                            "target_encoder": t_enc,
                            "feature_encoders": f_encs
                        }
                    except Exception as e:
                        st.error(f"Training error: {str(e)}")

        if st.session_state.trained_ml:
            m_state = st.session_state.trained_ml
            st.markdown(f"##### 🏆 Benchmark Leaderboard ({m_state['task_type'].title()})")
            st.dataframe(m_state["results_df"], width="stretch")

            if m_state["feat_plot"]:
                st.plotly_chart(m_state["feat_plot"], width="stretch")
            if m_state["diag_plot"]:
                st.plotly_chart(m_state["diag_plot"], width="stretch")

    # Interactive What-If Scenario Simulator
    if st.session_state.trained_ml:
        st.markdown("---")
        st.markdown("#### 🔮 Interactive 'What-If' Prediction Simulator")
        st.caption("Adjust operational parameters below to see the best-performing model predict outcomes in real time.")

        m_state = st.session_state.trained_ml
        active_model = m_state["models_dict"][m_state["best_model_name"]]
        
        sim_cols = st.columns(min(len(m_state["features"]), 4))
        user_inputs = {}

        for idx, feat in enumerate(m_state["features"]):
            target_slot = sim_cols[idx % len(sim_cols)]
            with target_slot:
                if pd.api.types.is_numeric_dtype(working_df[feat]):
                    f_min = float(working_df[feat].min())
                    f_max = float(working_df[feat].max())
                    f_med = float(working_df[feat].median())
                    user_inputs[feat] = st.slider(feat, min_value=f_min, max_value=f_max, value=f_med)
                else:
                    options = working_df[feat].dropna().unique().tolist()
                    user_inputs[feat] = st.selectbox(feat, options)

        if st.button("⚡ Run Simulation", type="primary"):
            row_payload = pd.DataFrame([user_inputs])
            for feat, enc in m_state["feature_encoders"].items():
                if feat in row_payload.columns:
                    val_str = str(row_payload[feat].iloc[0])
                    if val_str in enc.classes_:
                        row_payload[feat] = enc.transform([val_str])[0]
                    else:
                        row_payload[feat] = 0

            pred = active_model.predict(row_payload)[0]

            if m_state["task_type"] == "classification" and m_state["target_encoder"]:
                label = m_state["target_encoder"].inverse_transform([pred])[0]
                st.success(f"🎯 **Simulated Outcome for {m_state['target_col']}**: `{label}` (Algorithm: {m_state['best_model_name']})")
            else:
                st.success(f"🎯 **Simulated Outcome for {m_state['target_col']}**: `{pred:,.2f}` (Algorithm: {m_state['best_model_name']})")


# ----------------------------------------------------
# TAB 8: EXPORT & REPORTS
# ----------------------------------------------------
with tab_export:
    st.markdown("### 📥 Export & Academic Report Center")
    st.caption("Download cleaned dataset and standalone executive intelligence reports.")

    e1, e2, e3 = st.columns(3)

    with e1:
        st.markdown("##### 📄 Export Cleaned CSV")
        st.caption("Comma-separated values format for database import or external scripts.")
        csv_data = export_to_csv(working_df)
        st.download_button(
            label="⬇️ Download CSV",
            data=csv_data,
            file_name="Autonomous_DA_Cleaned_Dataset.csv",
            mime="text/csv"
        )

    with e2:
        st.markdown("##### 📑 Export Styled Excel (.xlsx)")
        st.caption("Structured Excel workbook with bold headers and auto-sized columns.")
        try:
            excel_data = export_to_excel(working_df)
            st.download_button(
                label="⬇️ Download Excel (.xlsx)",
                data=excel_data,
                file_name="Autonomous_DA_Cleaned_Dataset.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            )
        except Exception as exc:
            st.warning(f"Could not generate Excel export: {exc}")

    with e3:
        st.markdown("##### 🌐 Executive HTML Report")
        st.caption("Complete standalone HTML report containing KPIs, schema, and insights.")
        ml_bench_table = st.session_state.trained_ml["results_df"] if st.session_state.trained_ml else None
        html_rep = generate_executive_html_report(working_df, meta, insights_list, ml_bench_table)
        st.download_button(
            label="⬇️ Download Executive Report (.html)",
            data=html_rep.encode("utf-8"),
            file_name="Autonomous_DA_Executive_Intelligence_Report.html",
            mime="text/html"
        )
