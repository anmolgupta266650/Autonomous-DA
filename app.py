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
    st.markdown(
        '<div style="max-width: 620px; margin: 30px auto 16px auto; text-align: center;">'
        '<div style="font-size: 3.2rem; margin-bottom: 6px;">⚡</div>'
        '<h1 style="color: #ffffff; font-weight: 800; font-size: 2.3rem; margin-bottom: 6px;">Autonomous DA Enterprise</h1>'
        '<p style="color: #94a3b8; font-size: 1.05rem;">Role-Based Access Control (RBAC) & Secure Data Intelligence Platform</p>'
        '</div>',
        unsafe_allow_html=True
    )

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
# 4-HUB CONSOLIDATED ENTERPRISE NAVIGATION
# ==============================================================
home_page = st.Page("pages/1_Home.py", title="Executive Launchpad", icon="⚡", default=True)
data_page = st.Page("pages/2_Data_Studio.py", title="Data & BI Studio", icon="📊")
ai_page = st.Page("pages/3_AI_Hub.py", title="AI Intelligence & Copilot", icon="🤖")
finance_page = st.Page("pages/4_Finance_Science.py", title="Finance & Science Studios", icon="💼")
export_page = st.Page("pages/5_Executive_Export.py", title="Executive Reports & Decks", icon="📥")

if not st.session_state.get("authenticated", False):
    login_page = st.Page(render_login_screen, title="Enterprise Login", icon="🔒")
    pg = st.navigation([login_page], position="hidden")
else:
    role = st.session_state.user.get("role", "admin")
    if role == "admin":
        pg = st.navigation({
            "Command Center": [home_page],
            "Flagship Studios": [data_page, ai_page, finance_page, export_page]
        })
    elif role == "accountant":
        pg = st.navigation({
            "Command Center": [home_page],
            "Specialized Workspaces": [finance_page, data_page, export_page]
        })
    elif role == "researcher":
        pg = st.navigation({
            "Command Center": [home_page],
            "Specialized Workspaces": [finance_page, ai_page, export_page]
        })
    else:  # viewer
        pg = st.navigation({
            "Command Center": [home_page],
            "Executive Views": [data_page, export_page]
        })

pg.run()
