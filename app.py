import os
import streamlit as st
from modules.common_ui import init_app_state
from modules.db_manager import authenticate_user

# Master Page Configuration
st.set_page_config(
    page_title="Autonomous DA | Enterprise Analytics & Research Platform",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)


# Inject custom styling across the application
def load_custom_css():
    css_path = os.path.join(os.path.dirname(__file__), "assets", "style.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)


load_custom_css()
init_app_state()


def render_login_screen():
    st.markdown("""
    <div style="max-width: 620px; margin: 30px auto 16px auto; text-align: center;">
        <div style="font-size: 3.2rem; margin-bottom: 6px;">⚡</div>
        <h1 style="color: #ffffff; font-weight: 800; font-size: 2.3rem; margin-bottom: 6px;">Autonomous DA Enterprise</h1>
        <p style="color: #94a3b8; font-size: 1.05rem;">Role-Based Access Control (RBAC) & Secure Data Intelligence Platform</p>
    </div>
    """, unsafe_allow_html=True)

    lc1, lc2, lc3 = st.columns([1, 2.2, 1])
    with lc2:
        with st.container(border=True):
            st.markdown("#### 🔐 Enterprise Single Sign-On")
            username_input = st.text_input("Username", placeholder="e.g. admin, cfo_accountant, researcher, executive")
            password_input = st.text_input("Password", type="password", placeholder="Enter password")

            if st.button("🚀 Sign In to Platform", type="primary", use_container_width=True):
                user = authenticate_user(username_input, password_input)
                if user:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.session_state.last_action_msg = f"Signed in successfully as {user['full_name']}!"
                    st.rerun()
                else:
                    st.error("Invalid credentials. Please verify your username and password.")

            st.write("")
            st.markdown("##### ⚡ Quick 1-Click Role Switcher")
            st.caption("Select a pre-seeded enterprise role to preview authorized access permissions:")

            r1, r2 = st.columns(2)
            with r1:
                if st.button("👑 Administrator\n(Full Platform)", key="demo_admin", use_container_width=True):
                    u = authenticate_user("admin", "admin123")
                    st.session_state.authenticated = True
                    st.session_state.user = u
                    st.session_state.last_action_msg = f"Signed in as {u['full_name']} (Administrator)"
                    st.rerun()

                if st.button("💼 CFO / Accountant\n(Tally & Fraud Audits)", key="demo_cfo", use_container_width=True):
                    u = authenticate_user("cfo_accountant", "tally123")
                    st.session_state.authenticated = True
                    st.session_state.user = u
                    st.session_state.last_action_msg = f"Signed in as {u['full_name']} (Accountant)"
                    st.rerun()

            with r2:
                if st.button("🔬 Research Scientist\n(APA Papers & AutoML)", key="demo_sci", use_container_width=True):
                    u = authenticate_user("researcher", "science123")
                    st.session_state.authenticated = True
                    st.session_state.user = u
                    st.session_state.last_action_msg = f"Signed in as {u['full_name']} (Researcher)"
                    st.rerun()

                if st.button("📊 Executive Viewer\n(Dashboards & Decks)", key="demo_exec", use_container_width=True):
                    u = authenticate_user("executive", "exec123")
                    st.session_state.authenticated = True
                    st.session_state.user = u
                    st.session_state.last_action_msg = f"Signed in as {u['full_name']} (Executive Viewer)"
                    st.rerun()


# ==============================================================
# OFFICIAL MULTI-PAGE WEBSITE NAVIGATION & ROUTING
# ==============================================================
home_page = st.Page("pages/1_Home.py", title="Home & Overview", icon="🏠", default=True)
copilot_page = st.Page("pages/11_AI_Data_Copilot.py", title="AI Data Copilot", icon="💬")
pbi_page = st.Page("pages/4_PowerBI_Dashboard.py", title="Power BI Dashboard", icon="🖥️")
excel_page = st.Page("pages/5_Excel_Pivot.py", title="Excel & Pivot Studio", icon="📊")
sheet_page = st.Page("pages/6_Smart_Spreadsheet.py", title="Smart Spreadsheet", icon="📋")
tally_page = st.Page("pages/2_Tally_Finance.py", title="Tally Accounting", icon="💼")
research_page = st.Page("pages/3_Academic_Research.py", title="Scientific Research", icon="🔬")
automl_page = st.Page("pages/8_Predictive_AutoML.py", title="Predictive AI & AutoML", icon="🤖")
cleaner_page = st.Page("pages/7_Data_Cleaning.py", title="Data Cleaning & Features", icon="🧹")
db_page = st.Page("pages/9_Database_Checkpoints.py", title="Database & Stages", icon="💾")
export_page = st.Page("pages/10_Export_Reports.py", title="Export & Reports", icon="📥")

if not st.session_state.get("authenticated", False):
    login_page = st.Page(render_login_screen, title="Enterprise Login", icon="🔒")
    pg = st.navigation([login_page], position="hidden")
else:
    role = st.session_state.user.get("role", "admin")
    if role == "admin":
        pg = st.navigation({
            "Overview & AI Assistant": [home_page, copilot_page],
            "Business Intelligence & Excel": [pbi_page, excel_page, sheet_page],
            "Specialized Studios": [tally_page, research_page, automl_page],
            "Data Engineering & Storage": [cleaner_page, db_page, export_page]
        })
    elif role == "accountant":
        pg = st.navigation({
            "Overview & AI Assistant": [home_page, copilot_page],
            "Financial Accounting & Fraud Audit": [tally_page, excel_page, sheet_page],
            "Executive Reports & Briefings": [export_page]
        })
    elif role == "researcher":
        pg = st.navigation({
            "Overview & AI Assistant": [home_page, copilot_page],
            "Scientific Research & Predictive AI": [research_page, automl_page],
            "Data Engineering & Spreadsheet": [cleaner_page, sheet_page],
            "Academic Manuscripts & Reports": [export_page]
        })
    else:  # viewer
        pg = st.navigation({
            "Overview & AI Assistant": [home_page, copilot_page],
            "Executive Dashboards & Pivots": [pbi_page, excel_page],
            "Briefings & 16:9 Slide Decks": [export_page]
        })

pg.run()
