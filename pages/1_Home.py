import streamlit as st
import pandas as pd
from modules.common_ui import render_sidebar_data_controls, render_page_header
from modules.autopilot_engine import run_autonomous_audit

working_df = render_sidebar_data_controls()
render_page_header("🏠 Home & Overview", working_df)

# Hero 1-Click Auto-Pilot Banner
st.markdown("""
<div class="autopilot-hero">
    <div class="autopilot-title">🚀 1-Click Autonomous Auto-Pilot</div>
    <div class="autopilot-sub">Don't know where to start? Let the engine automatically clean data, detect financial or research patterns, run statistical tests, generate top charts, and assemble an executive audit deck in seconds.</div>
</div>
""", unsafe_allow_html=True)

ap_c1, ap_c2 = st.columns([1, 3])
with ap_c1:
    if st.button("⚡ Run 1-Click Auto-Pilot Audit", type="primary", use_container_width=True, help="Executes an end-to-end audit with zero configuration required."):
        with st.spinner("Autonomous Engine is analyzing and auditing your dataset..."):
            st.session_state.autopilot_result = run_autonomous_audit(working_df, st.session_state.dataset_name)
            st.session_state.last_action_msg = "Autonomous 1-Click Audit completed successfully!"
            st.rerun()

# Display Auto-Pilot Results if generated
if st.session_state.autopilot_result:
    ap_res = st.session_state.autopilot_result
    st.markdown(f"""
    <div class="plain-box">
        <span class="plain-badge">AUTONOMOUS AUDIT RESULTS [{ap_res['domain_tag'].upper()}]</span>
        <h4 style="margin: 6px 0; color: #f8fafc;">{ap_res['cleaning_summary']}</h4>
        <p style="margin: 0; color: #cbd5e1;">{ap_res['plain_english_takeaway']}</p>
    </div>
    """, unsafe_allow_html=True)

    if ap_res.get("exec_kpis"):
        kpi_cols = st.columns(len(ap_res["exec_kpis"]))
        for idx, kpi in enumerate(ap_res["exec_kpis"]):
            with kpi_cols[idx]:
                st.markdown(f"""
                <div class="kpi-box">
                    <div class="kpi-label">{kpi['label']}</div>
                    <div class="kpi-number">{kpi['val']}</div>
                    <div class="kpi-subtext highlight">{kpi['sub']}</div>
                </div>
                """, unsafe_allow_html=True)

    st.write("")
    c_r1, c_r2 = st.columns(2)
    with c_r1:
        if "cat_bar" in ap_res.get("exec_charts", {}):
            st.plotly_chart(ap_res["exec_charts"]["cat_bar"], width="stretch", key="home_cat_bar_plot")
    with c_r2:
        if ap_res.get("waterfall_fig"):
            st.plotly_chart(ap_res["waterfall_fig"], width="stretch", key="home_waterfall_plot")
        elif "trend" in ap_res.get("exec_charts", {}):
            st.plotly_chart(ap_res["exec_charts"]["trend"], width="stretch", key="home_trend_plot")

    st.markdown("---")

# Goal-Based Interactive Studio Selector
st.markdown("### 🎯 Dedicated Application Pages")
st.caption("Navigate to any specialized page from the sidebar menu, or click any studio below:")
st.write("")

def safe_switch_page(target_page_path: str, fallback_title: str):
    try:
        st.switch_page(target_page_path)
    except Exception:
        st.warning(f"🔒 Access Restricted: Your role ({st.session_state.get('user', {}).get('role', 'current')}) does not have permission to access {fallback_title}.")

row1_c1, row1_c2, row1_c3 = st.columns(3)

with row1_c1:
    st.markdown("""
    <div class="hub-card">
        <span class="hub-icon">💼</span>
        <div class="hub-title">Tally & Financial Accounting</div>
        <div class="hub-desc">Analyze Tally ledgers, daybooks, P&L statements, debtor aging (0-30, 31-60, 90+ days), and corporate waterfall financial flows.</div>
        <span class="hub-tag">Accountants & CFOs</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Tally Page ➔", key="btn_tally", type="secondary", use_container_width=True):
        safe_switch_page("pages/2_Tally_Finance.py", "Tally Financial Accounting")

with row1_c2:
    st.markdown("""
    <div class="hub-card">
        <span class="hub-icon">🔬</span>
        <div class="hub-title">Academic & Scientific Research</div>
        <div class="hub-desc">Auto-formulate research questions, testable hypotheses (H₀, H₁), compute Welch's t-tests, ANOVA, OLS regressions, and auto-draft APA 7th papers.</div>
        <span class="hub-tag">Researchers & Students</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Research Page ➔", key="btn_research", type="secondary", use_container_width=True):
        safe_switch_page("pages/3_Academic_Research.py", "Academic & Scientific Research")

with row1_c3:
    st.markdown("""
    <div class="hub-card">
        <span class="hub-icon">🖥️</span>
        <div class="hub-title">Power BI Executive Dashboard</div>
        <div class="hub-desc">Generate executive KPI summary cards, 4-chart executive grid dashboards, and design any custom chart with our visual builder studio.</div>
        <span class="hub-tag">Executives & Analysts</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Power BI Page ➔", key="btn_pbi_dash", type="secondary", use_container_width=True):
        safe_switch_page("pages/4_PowerBI_Dashboard.py", "Power BI Executive Dashboard")

st.write("")
row2_c1, row2_c2, row2_c3 = st.columns(3)

with row2_c1:
    st.markdown("""
    <div class="hub-card">
        <span class="hub-icon">📊</span>
        <div class="hub-title">Excel & Pivot Matrix Studio</div>
        <div class="hub-desc">Build dynamic multi-dimensional pivot tables with totals, and calculate DAX measures (% contribution, YTD cumulative, moving averages).</div>
        <span class="hub-tag">Excel & BI Power Users</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Excel Pivot Page ➔", key="btn_pivot", type="secondary", use_container_width=True):
        safe_switch_page("pages/5_Excel_Pivot.py", "Excel & Pivot Studio")

with row2_c2:
    st.markdown("""
    <div class="hub-card">
        <span class="hub-icon">🧹</span>
        <div class="hub-title">Data Cleaning & Feature Studio</div>
        <div class="hub-desc">Impute missing cells, eliminate duplicate rows, cast types, clamp statistical outliers (IQR/Z-score), and construct mathematical formulas.</div>
        <span class="hub-tag">Data Preparation</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Data Cleaning Page ➔", key="btn_cleaner", type="secondary", use_container_width=True):
        safe_switch_page("pages/7_Data_Cleaning.py", "Data Cleaning & Features")

with row2_c3:
    st.markdown("""
    <div class="hub-card">
        <span class="hub-icon">🤖</span>
        <div class="hub-title">Predictive AI & AutoML Studio</div>
        <div class="hub-desc">Automatically benchmark Machine Learning models (Classification & Regression), inspect feature importances, and run What-If simulations.</div>
        <span class="hub-tag">Data Science</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Predictive AI Page ➔", key="btn_automl", type="secondary", use_container_width=True):
        safe_switch_page("pages/8_Predictive_AutoML.py", "Predictive AI & AutoML")

st.write("")
row3_c1, row3_c2, row3_c3 = st.columns(3)

with row3_c1:
    st.markdown("""
    <div class="hub-card">
        <span class="hub-icon">💬</span>
        <div class="hub-title">AI Data Copilot</div>
        <div class="hub-desc">Chat with your data in plain English. Ask questions, discover rankings, correlations, and get instant interactive charts.</div>
        <span class="hub-tag">Natural Language AI</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Chat with Data Copilot ➔", key="btn_copilot", type="secondary", use_container_width=True):
        safe_switch_page("pages/11_AI_Data_Copilot.py", "AI Data Copilot")

with row3_c2:
    st.markdown("""
    <div class="hub-card">
        <span class="hub-icon">📋</span>
        <div class="hub-title">Smart Spreadsheet & Grid Editor</div>
        <div class="hub-desc">Edit spreadsheet cells directly in your browser, insert or delete records, and commit changes as persistent SQLite checkpoints.</div>
        <span class="hub-tag">In-Browser Editing</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Spreadsheet Editor ➔", key="btn_sheet_editor", type="secondary", use_container_width=True):
        safe_switch_page("pages/6_Smart_Spreadsheet.py", "Smart Spreadsheet Editor")

with row3_c3:
    st.markdown("""
    <div class="hub-card">
        <span class="hub-icon">📥</span>
        <div class="hub-title">Reports & 16:9 Slide Decks</div>
        <div class="hub-desc">Generate 1-click executive presentation slide decks (.html / print to PDF), publication-ready APA papers, and styled Excel exports.</div>
        <span class="hub-tag">Executive Export</span>
    </div>
    """, unsafe_allow_html=True)
    if st.button("Go to Reports & Decks ➔", key="btn_exports_home", type="secondary", use_container_width=True):
        safe_switch_page("pages/10_Export_Reports.py", "Export & Reports")

