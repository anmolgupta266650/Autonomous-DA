import os
import streamlit as st
import pandas as pd
from modules.data_loader import (
    load_file, get_excel_sheet_names, get_dataset_metadata,
    get_available_real_datasets, load_real_dataset
)
from modules.db_manager import (
    init_db, list_projects, create_project, save_checkpoint,
    list_checkpoints, load_checkpoint, get_latest_checkpoint
)
from modules.template_generator import get_sample_templates
from modules.live_connectors import (
    load_google_sheet_by_url, query_sqlite_database, probe_local_tally_endpoint,
    load_remote_rest_api
)


def load_custom_css():
    """Injects custom CSS styling globally."""
    css_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


def init_app_state():
    """Initializes and ensures all global session states persist across pages."""
    load_custom_css()
    init_db()

    if "project_id" not in st.session_state:
        st.session_state.project_id = "proj-default"
    if "project_name" not in st.session_state:
        st.session_state.project_name = "Global Enterprise Project"
    if "current_stage" not in st.session_state:
        st.session_state.current_stage = "Raw Ingestion"
    if "raw_df" not in st.session_state:
        st.session_state.raw_df = None
    if "df" not in st.session_state:
        st.session_state.df = None
    if "audit_log" not in st.session_state:
        st.session_state.audit_log = []
    if "dataset_name" not in st.session_state:
        st.session_state.dataset_name = "Global Superstore Sales (1,200 Transactions)"
    if "trained_ml" not in st.session_state:
        st.session_state.trained_ml = None
    if "last_action_msg" not in st.session_state:
        st.session_state.last_action_msg = None
    if "active_research_paper" not in st.session_state:
        st.session_state.active_research_paper = None
    if "autopilot_result" not in st.session_state:
        st.session_state.autopilot_result = None
    if "reports_exported_count" not in st.session_state:
        st.session_state.reports_exported_count = 0
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "user" not in st.session_state:
        st.session_state.user = None

    projects_in_db = list_projects()
    if not projects_in_db:
        create_project("proj-default", "Global Enterprise Project", "Default persistent multi-stage analytics project")

    if st.session_state.df is None:
        real_data = load_real_dataset("🛒 Global Superstore Sales (1,200 transactions)")
        st.session_state.raw_df = real_data.copy()
        st.session_state.df = real_data.copy()
        st.session_state.audit_log.append("Initialized authentic Global Superstore commercial dataset.")
        save_checkpoint(st.session_state.project_id, "Raw Ingestion", real_data, "Auto-initialized default benchmark dataset")


def render_sidebar_data_controls():
    """Renders persistent data upload, project switcher, and template controls on the sidebar."""
    init_app_state()
    with st.sidebar:
        st.markdown("### ⚡ Autonomous DA")
        st.caption("Enterprise Multi-Page Analytics Platform")
        st.markdown("---")

        if st.session_state.get("authenticated", False) and st.session_state.get("user"):
            u = st.session_state.user
            role = u.get("role", "viewer")
            role_color = {
                "admin": "#a855f7",
                "accountant": "#10b981",
                "researcher": "#06b6d4",
                "viewer": "#3b82f6"
            }.get(role, "#94a3b8")
            role_label = {
                "admin": "👑 Administrator",
                "accountant": "💼 CFO / Accountant",
                "researcher": "🔬 Research Scientist",
                "viewer": "📊 Executive Viewer"
            }.get(role, role.title())

            st.markdown(
                '<div style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(255, 255, 255, 0.1); border-radius: 10px; padding: 10px 14px; margin-bottom: 8px;">'
                '<div style="font-size: 0.72rem; color: #94a3b8; text-transform: uppercase; font-weight: 700;">SIGNED IN AS</div>'
                f'<div style="font-size: 0.95rem; font-weight: 800; color: #f8fafc; margin: 2px 0;">{u.get("full_name", "Enterprise User")}</div>'
                f'<div style="display: inline-block; background: {role_color}22; color: {role_color}; border: 1px solid {role_color}55; border-radius: 9999px; padding: 2px 10px; font-size: 0.72rem; font-weight: 700; margin-top: 4px;">{role_label}</div>'
                '</div>',
                unsafe_allow_html=True
            )
            if st.button("🚪 Sign Out", key="sb_signout_btn", use_container_width=True):
                st.session_state.authenticated = False
                st.session_state.user = None
                st.rerun()

            st.markdown("---")

        # 1. Database Project Switcher
        st.markdown("#### 💾 Project Database")
        all_projs = list_projects()
        proj_map = {f"{p['name']} ({p['id'][:8]})": p['id'] for p in all_projs}
        
        current_key_idx = 0
        proj_labels = list(proj_map.keys())
        for idx, (label, pid) in enumerate(proj_map.items()):
            if pid == st.session_state.project_id:
                current_key_idx = idx
                break

        selected_proj_label = st.selectbox("Active Project", proj_labels, index=current_key_idx if proj_labels else 0, help="Select project stored in SQLite database.")
        if proj_labels and proj_map[selected_proj_label] != st.session_state.project_id:
            new_pid = proj_map[selected_proj_label]
            st.session_state.project_id = new_pid
            res = get_latest_checkpoint(new_pid)
            if res:
                loaded_df, meta_c = res
                st.session_state.df = loaded_df.copy()
                st.session_state.raw_df = loaded_df.copy()
                st.session_state.current_stage = meta_c.get("stage_name", "Restored")
                st.session_state.last_action_msg = f"Switched to project checkpoint '{meta_c.get('stage_name')}'"
                st.rerun()

        st.markdown("---")

        # 2. Data Ingestion
        st.markdown("#### 📁 Active Data Source")
        ingestion_mode = st.radio(
            "Source Mode",
            ["Benchmark Datasets", "Upload File", "Live Connectors"],
            index=0,
            help="Load ready benchmark data, upload files, or link live data sources (Google Sheets, SQLite, Tally)."
        )

        if ingestion_mode == "Benchmark Datasets":
            real_datasets = get_available_real_datasets()
            selected_real = st.selectbox(
                "Select Benchmark",
                list(real_datasets.keys()),
                index=0
            )
            if st.button("📥 Ingest Dataset", type="primary", use_container_width=True):
                loaded_df = load_real_dataset(selected_real)
                st.session_state.raw_df = loaded_df.copy()
                st.session_state.df = loaded_df.copy()
                st.session_state.dataset_name = selected_real
                st.session_state.audit_log = [f"Loaded dataset: {selected_real}"]
                st.session_state.trained_ml = None
                st.session_state.autopilot_result = None
                st.session_state.current_stage = "Raw Ingestion"
                save_checkpoint(st.session_state.project_id, "Raw Ingestion", loaded_df, f"Ingested {selected_real}")
                st.session_state.last_action_msg = f"Successfully loaded {selected_real}!"
                st.rerun()
        elif ingestion_mode == "Live Connectors":
            conn_type = st.selectbox("Connector Type", [
                "🌐 Google Sheets URL",
                "📡 Live REST API Endpoint",
                "🗄️ SQLite Database",
                "💼 Tally Prime (Local)"
            ])
            if conn_type == "🌐 Google Sheets URL":
                sheet_url = st.text_input("Google Sheet Link", placeholder="https://docs.google.com/spreadsheets/d/...")
                st.caption("Must be shared as 'Anyone with link can view'")
                if st.button("⚡ Fetch Google Sheet", type="primary", use_container_width=True):
                    with st.spinner("Connecting to Google Sheets..."):
                        gs_df, gs_err = load_google_sheet_by_url(sheet_url)
                        if gs_err:
                            st.error(gs_err)
                        elif gs_df is not None:
                            st.session_state.raw_df = gs_df.copy()
                            st.session_state.df = gs_df.copy()
                            st.session_state.dataset_name = "Live Google Sheet"
                            st.session_state.audit_log = ["Ingested from Live Google Sheet URL"]
                            st.session_state.trained_ml = None
                            st.session_state.autopilot_result = None
                            st.session_state.current_stage = "Live Ingestion"
                            save_checkpoint(st.session_state.project_id, "Live Ingestion", gs_df, "Google Sheets live sync")
                            st.session_state.last_action_msg = f"Loaded {len(gs_df):,} rows from Google Sheets!"
                            st.rerun()

            elif conn_type == "📡 Live REST API Endpoint":
                api_url = st.text_input("REST API URL (JSON)", placeholder="https://api.coindesk.com/v1/bpi/currentprice.json")
                st.caption("Directly ingest and normalize JSON records from external public or internal microservice APIs.")
                if st.button("⚡ Ingest REST API", type="primary", use_container_width=True):
                    with st.spinner("Connecting to remote REST endpoint..."):
                        api_df, api_err = load_remote_rest_api(api_url)
                        if api_err:
                            st.error(api_err)
                        elif api_df is not None:
                            st.session_state.raw_df = api_df.copy()
                            st.session_state.df = api_df.copy()
                            st.session_state.dataset_name = f"API: {api_url.split('/')[-1] or 'Endpoint'}"
                            st.session_state.audit_log = [f"Ingested from REST API: {api_url[:35]}..."]
                            st.session_state.trained_ml = None
                            st.session_state.autopilot_result = None
                            st.session_state.current_stage = "Live API Ingestion"
                            save_checkpoint(st.session_state.project_id, "Live API Ingestion", api_df, f"REST sync: {api_url[:40]}")
                            st.session_state.last_action_msg = f"Imported {len(api_df):,} live records from REST API!"
                            st.rerun()

            elif conn_type == "🗄️ SQLite Database":
                db_file = st.text_input("Database Path", value="data/projects.db")
                sql_q = st.text_area("SQL Query", value="SELECT * FROM projects", height=70)
                if st.button("⚡ Run SQL Query", type="primary", use_container_width=True):
                    sql_df, sql_err = query_sqlite_database(db_file, sql_q)
                    if sql_err:
                        st.error(sql_err)
                    elif sql_df is not None:
                        st.session_state.raw_df = sql_df.copy()
                        st.session_state.df = sql_df.copy()
                        st.session_state.dataset_name = f"SQLite: {db_file}"
                        st.session_state.audit_log = [f"Queried SQLite: {sql_q[:30]}..."]
                        st.session_state.trained_ml = None
                        st.session_state.autopilot_result = None
                        st.session_state.current_stage = "SQL Query Ingestion"
                        save_checkpoint(st.session_state.project_id, "SQL Query Ingestion", sql_df, f"Query on {db_file}")
                        st.session_state.last_action_msg = f"Imported {len(sql_df):,} records via SQL query!"
                        st.rerun()

            elif conn_type == "💼 Tally Prime (Local)":
                tally_host = st.text_input("Tally Prime Host", value="http://localhost:9000")
                if st.button("🔌 Probe Tally Prime", use_container_width=True):
                    is_ok, msg = probe_local_tally_endpoint(tally_host)
                    if is_ok:
                        st.success(msg)
                    else:
                        st.warning(msg)
        else:
            uploaded_file = st.file_uploader(
                "Upload File (CSV, Excel, XML, JSON)",
                type=["csv", "xlsx", "xls", "json", "xml"]
            )
            with st.expander("📥 Download Blank Templates", expanded=False):
                templates = get_sample_templates()
                st.download_button("💼 Tally Ledger (.csv)", data=templates["tally_ledger"], file_name="Tally_Ledger_Template.csv", mime="text/csv")
                st.download_button("🛒 Sales & BI (.csv)", data=templates["sales_bi"], file_name="Sales_BI_Template.csv", mime="text/csv")
                st.download_button("🎓 Academic Survey (.csv)", data=templates["academic_research"], file_name="Academic_Survey_Template.csv", mime="text/csv")

            if uploaded_file is not None:
                sheet_choice = None
                if uploaded_file.name.lower().endswith((".xlsx", ".xls")):
                    sheets = get_excel_sheet_names(uploaded_file)
                    if len(sheets) > 1:
                        sheet_choice = st.selectbox("Select Excel Sheet", sheets)

                if st.button("⚡ Ingest Uploaded File", type="primary", use_container_width=True):
                    df_loaded, err = load_file(uploaded_file, sheet_name=sheet_choice)
                    if err:
                        st.error(err)
                    else:
                        st.session_state.raw_df = df_loaded.copy()
                        st.session_state.df = df_loaded.copy()
                        st.session_state.dataset_name = uploaded_file.name
                        st.session_state.audit_log = [f"Uploaded file: {uploaded_file.name}"]
                        st.session_state.trained_ml = None
                        st.session_state.autopilot_result = None
                        st.session_state.current_stage = "File Uploaded"
                        save_checkpoint(st.session_state.project_id, "File Uploaded", df_loaded, f"Uploaded {uploaded_file.name}")
                        st.session_state.last_action_msg = f"Uploaded {uploaded_file.name} successfully!"
                        st.rerun()

        st.markdown("---")

        # 3. Quick Global Slicer
        st.markdown("#### 🎯 Quick Dimension Filter")
        cat_columns = st.session_state.df.select_dtypes(include=["object", "category", "string"]).columns.tolist()
        filter_cat = None
        selected_category_val = "All"
        if cat_columns:
            filter_cat = st.selectbox("Filter Dimension", ["None"] + cat_columns)
            if filter_cat != "None":
                unique_vals = ["All"] + sorted(st.session_state.df[filter_cat].dropna().unique().tolist())[:30]
                selected_category_val = st.selectbox(f"Value for {filter_cat}", unique_vals)

        st.markdown("---")
        if st.button("↺ Reset Dataset to Original", use_container_width=True):
            if st.session_state.raw_df is not None:
                st.session_state.df = st.session_state.raw_df.copy()
                st.session_state.audit_log.append("Reset dataset to original imported state.")
                st.session_state.trained_ml = None
                st.session_state.autopilot_result = None
                st.session_state.current_stage = "Raw Ingestion"
                st.session_state.last_action_msg = "Dataset restored to original raw state."
                st.rerun()

    # Apply filter to working dataframe
    working = st.session_state.df.copy()
    if filter_cat and filter_cat != "None" and selected_category_val != "All":
        working = working[working[filter_cat] == selected_category_val].reset_index(drop=True)
    return working


def render_page_header(page_title: str, working_df: pd.DataFrame):
    """Renders consistent top navbar header on every page."""
    load_custom_css()
    meta = get_dataset_metadata(working_df)

    user_pill = ""
    if st.session_state.get("authenticated", False) and st.session_state.get("user"):
        u = st.session_state.user
        role_label = {
            "admin": "Admin",
            "accountant": "CFO / Accountant",
            "researcher": "Researcher",
            "viewer": "Viewer"
        }.get(u.get("role", "viewer"), "User")
        user_pill = f'<span class="nav-pill nav-pill-role"><span class="dot-indicator dot-purple"></span> Role: <strong>{role_label}</strong></span>'

    safe_dataset_name = (st.session_state.dataset_name[:24] if st.session_state.dataset_name else "Benchmark Data")
    rows_count = f"{meta.get('rows', 0):,}"
    health_score = meta.get('health_score', 100)

    health_dot = "dot-green" if health_score >= 80 else ("dot-amber" if health_score >= 50 else "dot-red")

    navbar_html = (
        '<div class="nexus-navbar">'
        '<div>'
        '<div class="brand-title-row">'
        '<h1 class="brand-title">⚡ Autonomous DA</h1>'
        f'<span class="brand-page-badge">{page_title}</span>'
        '</div>'
        '<p class="brand-tagline">No-Code Analytics, Tally Financials, Power BI & Scientific Research Platform</p>'
        '</div>'
        '<div class="nav-badges">'
        f'<span class="nav-pill"><span class="dot-indicator dot-green"></span> <strong>{safe_dataset_name}</strong> &nbsp;•&nbsp; <span style="color:#06b6d4;">{rows_count} rows</span> &nbsp;•&nbsp; <span class="dot-indicator {health_dot}"></span> {health_score}/100</span>'
        f'{user_pill}'
        '</div>'
        '</div>'
    )

    st.markdown(navbar_html, unsafe_allow_html=True)

    if st.session_state.last_action_msg:
        st.success(f"✅ {st.session_state.last_action_msg}")
        st.session_state.last_action_msg = None

