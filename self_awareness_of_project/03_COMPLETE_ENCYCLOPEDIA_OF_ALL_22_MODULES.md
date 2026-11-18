# 📘 Chapter 3: Complete Technical Encyclopedia of All 22 Modules

This chapter provides a comprehensive, function-by-function reference manual for all **22 backend modules** in the `modules/` directory.

---

## 1. `modules/automl_engine.py` — Predictive Machine Learning Engine
* **Purpose**: Automates the entire supervised machine learning workflow: task inference, feature preprocessing, model training, cross-validation, and feature importance extraction.
* **How It Works**:
  1. Inspects the target column to determine if the task is **Classification** (discrete labels, binary churn, tier) or **Regression** (continuous numbers, price, salary).
  2. Encodes categorical variables using `LabelEncoder`, imputes missing numerical values using median strategy, and standardizes continuous features with `StandardScaler`.
  3. Trains multiple scikit-learn models (Logistic Regression / Ridge, Random Forest, Gradient Boosting) using 5-fold cross-validation.
* **Key Functions**:
  * `detect_task_type(series_or_df, target_col=None) -> str`: Returns `'classification'` or `'regression'`.
  * `prepare_ml_data(df, target_col, feature_cols=None) -> (X, y, task_type, target_encoder, encoders)`: Prepares cleaned feature matrix $X$ and label vector $y$.
  * `train_and_evaluate_models(X, y, task_type) -> (results_df, trained_models, best_model_name, cm_fig, feat_fig, test_data)`: Returns evaluation metrics leaderboard, confusion matrix figure, and feature importance plot.

---

## 2. `modules/autopilot_engine.py` — 1-Click Autonomous Audit Engine
* **Purpose**: Orchestrates end-to-end zero-configuration analysis for first-time users.
* **How It Works**: Analyzes column headers using regex keyword scoring to tag the dataset into one of 4 domains (*Finance*, *Sales*, *Clinical*, *Academic*). Automatically cleans nulls and generates domain-specific charts.
* **Key Functions**:
  * `run_autonomous_audit(df, dataset_name) -> dict`: Returns a unified dictionary containing cleaning statistics, domain classification, plain-English takeaway, executive KPIs, and pre-computed Plotly figures.

---

## 3. `modules/bi_visualizer.py` — Executive Business Intelligence & Chart Engine
* **Purpose**: High-level visualizer producing publication-quality Plotly charts and automated 4-grid executive dashboards.
* **How It Works**: Maps user parameters to Plotly Express and Graph Objects, applying dark cyber themes with transparent backgrounds and automated responsive formatting.
* **Key Functions**:
  * `build_bi_chart(df, chart_type, x_col, y_col=None, color_col=None, aggregation='Sum', ...) -> go.Figure`: Renders Bar, Line, Area, Scatter, Treemap, Donut, Sunburst, Box, and Violin plots.
  * `build_executive_dashboard_charts(df) -> (charts_dict, kpi_list)`: Automatically selects top dimensions and metrics to construct a cohesive 4-chart executive grid.

---

## 4. `modules/business_insights.py` — Strategic Insight Generation Engine
* **Purpose**: Translates dry statistical numbers into actionable business observations for executive leaders.
* **How It Works**: Evaluates statistical skewness, revenue concentration (Pareto 80/20 principle), correlation strength, and missing data risks.
* **Key Functions**:
  * `generate_executive_insights(df) -> list[dict]`: Returns a structured list of insight cards categorized by `FINANCIAL`, `OPERATIONAL`, `DATA INTEGRITY`, and `STRATEGIC`.

---

## 5. `modules/common_ui.py` — Enterprise Navigation, Styling & App Bar
* **Purpose**: Enforces visual consistency, role-based navigation guards, and slimline navbar across all pages.
* **How It Works**: Injects `assets/style.css`, renders the 48px top navbar with live dataset and health score indicators, and manages session state.
* **Key Functions**:
  * `init_app_state()`: Initializes all session state variables (`df`, `raw_df`, `audit_log`, `project_id`, `authenticated`, `user`).
  * `render_page_header(page_title, working_df)`: Renders the top brand header, active dataset pill, row count, health score dot, and RBAC user badge.
  * `render_sidebar_data_controls() -> pd.DataFrame`: Manages data ingestion mode switcher (Benchmark, Presets, Upload, Live Connectors), project switcher, and global dimension slicer.

---

## 6. `modules/data_cleaner.py` — Deterministic Data Repair & Cleaning Sentinel
* **Purpose**: Implements non-destructive, audited data cleaning transformations.
* **How It Works**: Every operation creates a fresh copy of the DataFrame and logs the exact modification to `session_state.audit_log`.
* **Key Functions**:
  * `clean_missing_values(df, column, strategy='mean', fill_val=None) -> (df, message)`: Imputes missing values using Mean, Median, Mode, or Constant.
  * `remove_duplicates(df, subset_cols=None, keep='first') -> (df, message)`: Drops duplicate rows.
  * `cast_column_type(df, column, target_type) -> (df, message)`: Casts data types to int, float, str, datetime, or category.
  * `detect_and_handle_outliers(df, column, method='iqr', action='clamp') -> (df, message, count)`: Detects outliers using IQR or Z-score and performs Winsorization (clamping) or removal.
  * `rename_column(df, old_name, new_name) -> (df, message)`: Renames column headers.
  * `filter_dataset(df, column, operator, value) -> (df, message)`: Filters rows using logical operators.
  * `drop_selected_columns(df, columns) -> (df, message)`: Safely removes unneeded attributes.

---

## 7. `modules/data_copilot.py` — Conversational AI Copilot & Python Sandbox
* **Purpose**: Provides dual-mode conversational intelligence and an isolated Python code execution environment.
* **How It Works**:
  * *Heuristic Intent Router*: Regex-based intent classification matching questions to 10 analytical operations (outlier scan, top-N, category breakdown, monthly trend, summary stats).
  * *Sandboxed AST Execution*: Uses Python `exec()` with restricted builtins (stripping `open`, `eval`, `__import__`, `os`, `sys`) and redirects stdout to a buffer.
* **Key Functions**:
  * `ask_data_copilot(df, question, api_key=None) -> dict`: Dispatches queries to heuristic fallback or frontier cloud LLM.
  * `run_sandboxed_pandas_code(df, code_str) -> dict`: Executes Python code safely and captures stdout, output dataframe, and plotly figures.
  * `call_frontier_llm(df, question, api_key, provider='gemini') -> dict`: Calls Gemini 1.5 Flash or OpenAI GPT-4o-mini using user's BYOK key.

---

## 8. `modules/data_loader.py` — Ingestion Engine & Quality Profiler
* **Purpose**: Loads CSV, Excel, and JSON files, inspects Excel sheet names, and calculates structural metadata.
* **How It Works**: Handles encoding detection (UTF-8, Latin-1, CP1252), calculates missing cell rates, duplicate frequencies, and calculates a 0-100 **Data Health Score**.
* **Key Functions**:
  * `load_file(uploaded_file, sheet_name=None) -> pd.DataFrame`: Auto-detects format and loads file.
  * `get_dataset_metadata(df) -> dict`: Returns rows, cols, missing count, duplicate count, memory footprint, column type lists, and health score.
  * `get_available_real_datasets() -> dict`: Lists the 6 pre-seeded real benchmark datasets.
  * `load_real_dataset(name) -> pd.DataFrame`: Loads pre-seeded benchmark CSVs from `data/`.
  * `generate_sample_dataset(dataset_type='sales') -> pd.DataFrame`: Generates synthetic fallback data.

---

## 9. `modules/db_manager.py` — SQLite Database & RBAC Manager
* **Purpose**: Manages persistent storage in `data/projects.db` for user authentication, project sessions, and stage checkpoints.
* **How It Works**: Implements **salted SHA-256 password hashing** for user authentication and stores serialized DataFrame pickles for point-in-time recovery.
* **Key Functions**:
  * `init_db()`: Initializes tables (`users`, `projects`, `checkpoints`, `research_papers`).
  * `authenticate_user(username, password) -> dict`: Validates credentials against hashed passwords.
  * `save_checkpoint(project_id, stage_name, df, notes) -> int`: Saves an immutable snapshot of the active DataFrame.
  * `list_checkpoints(project_id) -> list[dict]`: Retrieves all saved checkpoints for a project.
  * `load_checkpoint(checkpoint_id) -> (df, meta)`: Deserializes and restores a previous DataFrame state.

---

## 10. `modules/eda_profiler.py` — Exploratory Data Analysis & Statistics
* **Purpose**: Computes comprehensive descriptive statistics, correlation matrices, and distribution histograms.
* **Key Functions**:
  * `get_detailed_statistics(df) -> pd.DataFrame`: Computes mean, std, median, IQR, skewness, and kurtosis.
  * `plot_feature_distribution(df, col) -> go.Figure`: Plots distribution with KDE curve and box plot.
  * `plot_correlation_heatmap(df) -> go.Figure`: Computes Pearson correlation heatmap for numeric features.
  * `plot_missing_values(df) -> go.Figure`: Renders a horizontal bar chart of missing percentages per column.

---

## 11. `modules/feature_builder.py` — Dynamic Feature Engineering Lab
* **Purpose**: Creates derived attributes to enhance machine learning model performance and business reporting.
* **Key Functions**:
  * `create_math_column(df, col_name, col1, op, col2) -> (df, message)`: Combines two columns with `+`, `-`, `*`, or `/`.
  * `apply_transform(df, col_name, src_col, transform_type) -> (df, message)`: Applies Logarithmic (`log1p`), Square Root, or Z-Score.
  * `extract_date_features(df, date_col, features) -> (df, message)`: Extracts Year, Month, Day, Day of Week, or Is_Weekend.
  * `create_binned_column(df, col_name, col, n_bins, strategy='quantile') -> (df, message)`: Discretizes continuous metrics into categorical bins.
  * `create_conditional_flag(df, col_name, col, op, threshold, true_val, false_val) -> (df, message)`: Creates conditional indicator flags.

---

## 12. `modules/forensic_auditor.py` — Benford's Law & Fraud Sentinel
* **Purpose**: Forensic audit suite for detecting manipulated accounting records, fabricated invoices, and kickbacks.
* **How It Works**:
  * Extracts the first significant digit ($d \in [1, 9]$) of transaction amounts.
  * Evaluates observed digit frequencies against **Benford's Law** ($P(d) = \log_{10}(1 + 1/d)$) via a **Chi-Square Goodness-of-Fit test**.
  * Flags duplicate payments (same vendor, identical sum) and clusters of exact round amounts (e.g. ₹50,000) used to bypass approval tiers.
* **Key Functions**:
  * `run_benfords_law_analysis(df, amount_col) -> (result_dict, figure)`: Computes $\chi^2$ statistic, $p$-value, maximum deviation digit, and dual-trace Plotly chart.
  * `detect_duplicate_transactions(df, party_col, amount_col, date_col=None) -> pd.DataFrame`: Flags duplicate disbursements.
  * `detect_round_number_spikes(df, amount_col) -> dict`: Flags abnormal concentrations of round numbers.

---

## 13. `modules/live_connectors.py` — External API & Database Connectors
* **Purpose**: Ingests live data from external URLs, REST APIs, Google Sheets, local SQLite, and Cloud SQL.
* **Key Functions**:
  * `load_google_sheet_by_url(url) -> (df, error)`: Transforms shareable Google Sheets URLs into direct CSV export endpoints.
  * `load_remote_rest_api(api_url) -> (df, error)`: Fetches and flattens live JSON endpoints into DataFrames.
  * `query_sqlite_database(db_path, sql_query) -> (df, error)`: Executes direct SQL queries on local databases.
  * `probe_local_tally_endpoint(host='http://localhost:9000') -> (bool, message)`: Tests if local Tally ERP is broadcasting XML.
  * `build_cloud_sql_connection_string(...) -> str`: Builds SQLAlchemy URI for PostgreSQL or MySQL.

---

## 14. `modules/module_test_registry.py` — Authority Evaluation & Diagnostic Registry
* **Purpose**: Powers the Authority Verification Hub on the Home page.
* **How It Works**: Maintains the catalog of 8 dedicated test presets, generates dirty test datasets with intentional corruptions (NaNs, duplicate rows, extreme outlier spikes), and runs the real-time engine self-test.
* **Key Functions**:
  * `generate_dirty_test_dataset(n_rows=500) -> pd.DataFrame`: Seeds data with exactly 35 missing cells, 15 duplicate rows, and 8 extreme outlier spikes for cleaning verification.
  * `load_test_preset_data(preset_key) -> (df, dataset_name, page_name)`: Loads the dedicated dataset and navigates to the target studio.
  * `run_system_health_diagnostic() -> list[dict]`: Executes real micro-benchmarks on 8 core subsystems and returns latency and PASS/FAIL status.

---

## 15. `modules/powerbi_excel_studio.py` — Power BI Pivot & DAX Engine
* **Purpose**: Implements multi-dimensional pivot matrices and DAX-style analytical measures.
* **How It Works**: Wraps `pd.pivot_table` with multi-index column flattening, preventing Streamlit rendering errors. Calculates running totals, percentage contributions, and moving averages.
* **Key Functions**:
  * `generate_pivot_table(df, index_cols, column_cols, value_col, agg_func='sum', add_margins=True) -> pd.DataFrame`: Creates pivot table with grand totals.
  * `compute_dax_measures(df, dimension_col, metric_col, measure_type, date_col=None) -> (df, formula_str)`: Computes % Contribution to Total, Cumulative Running Total, 3-Period Moving Average, or Period-over-Period Growth.
  * `build_powerbi_matrix_chart(summary_df, dim_col, metric_col, measure_col=None) -> go.Figure`: Renders dual-axis Power BI visual.

---

## 16. `modules/pptx_generator.py` — 10-Slide Microsoft PowerPoint (.pptx) Engine
* **Purpose**: Synthesizes a native, 10-slide 16:9 widescreen presentation in Microsoft PowerPoint (`.pptx`) format.
* **How It Works**: Uses `python-pptx` to construct slides with dark cyber theme colors (`#0f172a`, `#4f46e5`, `#38bdf8`), adding shapes, text boxes, data tables, and KPI callout blocks.
* **10 Slides Generated**:
  1. Title Slide (Project & Dataset metadata).
  2. Executive Problem Statement & Context.
  3. Key Performance Indicators (4 KPI scorecard tiles).
  4. Data Health & Ingestion Integrity (Missing & duplicate rates).
  5. Top-Performing Segments & Dimension Rankings.
  6. Financial Turnover & Margin Analysis (Waterfalls).
  7. Predictive Machine Learning Benchmarks (Accuracy scores).
  8. Risk Factors & Operational Vulnerabilities.
  9. Governance, Audit Lineage & SOX/GDPR Compliance.
  10. Strategic Recommendations & Boardroom Action Plan.
* **Key Function**:
  * `generate_executive_pptx_deck(df, dataset_name, meta=None, fin_metrics=None, insights=None) -> bytes`: Returns raw `.pptx` file bytes for instant download.

---

## 17. `modules/presentation_generator.py` — Interactive Web Presentation Deck
* **Purpose**: Generates an interactive, standalone HTML presentation deck viewable in any web browser.
* **Key Function**:
  * `generate_executive_presentation_deck(df, dataset_name, meta, fin_metrics, insights) -> str`: Returns standalone HTML presentation with slide navigation controls.

---

## 18. `modules/report_exporter.py` — Formatted Exporter & Governance Certificate
* **Purpose**: Exports formatted Excel spreadsheets, standalone HTML intelligence reports, and verifiable cryptographic compliance certificates.
* **Key Functions**:
  * `export_to_csv(df) -> bytes`: Returns UTF-8 CSV bytes.
  * `export_to_excel(df) -> bytes`: Returns styled Excel workbook with colored header rows and auto-adjusted column widths.
  * `generate_executive_html_report(df, metadata, insights, ml_results=None) -> str`: Builds standalone HTML report with KPI grid and insights.
  * `generate_compliance_certificate(df, dataset_name, project_id, audit_log=None, user=None) -> str`: Computes **SHA-256 data hash**, records transformation provenance, states SOX Section 404 & GDPR Article 30 compliance, and formats a printable sealed certificate.
  * `generate_simulated_alert_payload(df, dataset_name, alert_type='forensic') -> dict`: Generates corporate Slack Block Kit / Microsoft Teams JSON alert payloads.

---

## 19. `modules/research_studio.py` — Academic Science & APA 7th Edition Paper Generator
* **Purpose**: Executes rigorous parametric hypothesis testing and writes complete academic research papers.
* **Key Functions**:
  * `generate_research_questions(df) -> list[dict]`: Formulates null ($H_0$) and alternate ($H_1$) hypotheses.
  * `run_welch_ttest(df, metric, group_col) -> dict`: Runs Welch's t-test with Cohen's $d$ effect size ($p$-value, $t$-statistic).
  * `run_one_way_anova(df, metric, group_col) -> dict`: Runs One-Way ANOVA across multiple group levels ($F$-stat, $p$-val).
  * `run_ols_regression(df, dep_var, indep_vars) -> dict`: Runs multivariate ordinary least squares econometric regression ($R^2$, Adj $R^2$, coefficients, standard errors).
  * `generate_apa_research_paper(df, study_title, research_questions, stat_results) -> str`: Synthesizes an APA 7th Edition paper with Abstract, Intro, Methodology, Results with Markdown tables, Discussion, and References.

---

## 20. `modules/streaming_ingestor.py` — Real-Time Telemetry & Event Ingestion
* **Purpose**: Phase 2 component demonstrating real-time high-frequency streaming analytics and threshold breach detection.
* **Key Functions**:
  * `simulate_iot_financial_stream(n_events=60) -> pd.DataFrame`: Simulates real-time e-commerce / API orders with anomaly spikes.
  * `compute_sliding_window_metrics(stream_df, window_size=10) -> pd.DataFrame`: Calculates rolling means, volatility, and dynamic Z-Scores.
  * `detect_streaming_anomalies(stream_df, threshold_z=2.5) -> dict`: Evaluates threshold breaches and assigns a stream health status (`HEALTHY`, `WARNING`, `CRITICAL`).

---

## 21. `modules/tally_finance.py` — Corporate P&L & Accounts Receivable
* **Purpose**: Dedicated accounting engine for SME financial ledgers, Tally statements, and debtor aging.
* **Key Functions**:
  * `detect_financial_columns(df) -> dict`: Auto-detects revenue, expense, balance, and date columns using keyword matching.
  * `compute_tally_financial_metrics(df, rev_col, exp_col) -> dict`: Calculates Total Turnover, Cost of Goods Sold, Gross Profit, and Gross Margin %.
  * `build_financial_waterfall_chart(metrics) -> go.Figure`: Renders financial waterfall chart.
  * `build_debtor_aging_analysis(df, date_or_days_col, amount_col) -> (aging_summary, fig)`: Segments debtors into 0-30, 31-60, 61-90, and 90+ day overdue buckets.

---

## 22. `modules/template_generator.py` — Starter Data Template Generator
* **Purpose**: Provides pre-formatted, clean template CSVs for businesses starting from scratch.
* **Key Functions**:
  * `get_sample_templates() -> dict`: Returns starter templates for Tally Ledger, Commercial Sales BI, and Academic Survey.
  * `get_available_templates() -> dict`: Returns dictionary of template display titles.
  * `generate_template_data(template_name) -> pd.DataFrame`: Generates DataFrame from selected starter template.

---
*Autonomous DA Enterprise &bull; Chapter 3 &bull; Complete Technical Encyclopedia*
