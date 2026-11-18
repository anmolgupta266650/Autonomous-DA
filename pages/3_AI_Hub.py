import streamlit as st
import pandas as pd
import numpy as np
from modules.common_ui import render_sidebar_data_controls, render_page_header
from modules.data_copilot import ask_data_copilot, run_sandboxed_pandas_code
from modules.autopilot_engine import run_autonomous_audit
from modules.automl_engine import detect_task_type, prepare_ml_data, train_and_evaluate_models
from modules.data_loader import get_dataset_metadata
from modules.db_manager import save_checkpoint

working_df = render_sidebar_data_controls()
render_page_header("🤖 AI Intelligence & Copilot", working_df)

meta = get_dataset_metadata(working_df)

st.markdown("### 🤖 Flagship AI Intelligence & Copilot Hub")
st.caption("Conversational AI Copilot, sandboxed Python Code Interpreter, 1-Click Autonomous Audits, and Predictive Machine Learning.")

tab_copilot, tab_sandbox, tab_autopilot, tab_automl = st.tabs([
    "💬 Conversational Data Copilot",
    "🧪 Python Code Interpreter Sandbox",
    "🚀 1-Click Autonomous Auto-Pilot",
    "🤖 Predictive AutoML Engine"
])

# ==============================================================
# TAB 1: CONVERSATIONAL COPILOT
# ==============================================================
with tab_copilot:
    st.markdown("##### 💬 AI Data Copilot — Conversational Analytics")
    st.caption("Ask questions in plain English. The Copilot detects trends, outliers, rankings, and generates responsive charts.")

    if "copilot_messages" not in st.session_state:
        st.session_state.copilot_messages = [
            {
                "role": "assistant",
                "content": f"Hello! I am your AI Data Copilot. I'm connected to your active dataset with **{len(working_df):,} records** and **{len(working_df.columns)} columns**. What would you like to explore?",
                "data": None,
                "fig": None,
                "code": None
            }
        ]

    num_cols = working_df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = working_df.select_dtypes(include=["object", "category", "string"]).columns.tolist()

    suggested_queries = ["How many total records?"]
    if num_cols and cat_cols:
        suggested_queries.append(f"Top 5 {cat_cols[0]} by {num_cols[0]}")
        suggested_queries.append(f"Total {num_cols[0]} by {cat_cols[0]}")
        suggested_queries.append(f"Flag outliers in {num_cols[0]}")
    if len(num_cols) >= 2:
        suggested_queries.append(f"Correlation between {num_cols[0]} and {num_cols[1]}")

    st.markdown("##### 💡 Suggested Questions")
    s_cols = st.columns(len(suggested_queries[:4]))
    clicked_prompt = None
    for i, sq in enumerate(suggested_queries[:4]):
        with s_cols[i]:
            if st.button(sq, key=f"aihub_sq_btn_{i}", use_container_width=True):
                clicked_prompt = sq

    top_act_col, clr_col = st.columns([5, 1])
    with top_act_col:
        with st.expander("🔑 Optional Frontier AI Model (Google Gemini / OpenAI)", expanded=False):
            st.caption("Provide an optional API key to unlock frontier LLM zero-shot reasoning. If left empty, Copilot runs on our built-in local analytical engine with zero API costs.")
            user_llm_key = st.text_input("API Key (Gemini API Key or OpenAI `sk-...`)", type="password", key="aihub_user_llm_key")
    with clr_col:
        if st.button("🧹 Clear Chat", key="aihub_copilot_clear", use_container_width=True):
            st.session_state.copilot_messages = [
                {
                    "role": "assistant",
                    "content": f"Chat history cleared. Active dataset contains **{len(working_df):,} records**. How can I help?",
                    "data": None,
                    "fig": None,
                    "code": None
                }
            ]
            st.rerun()

    # Render Chat History
    for idx, msg in enumerate(st.session_state.copilot_messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("fig") is not None:
                st.plotly_chart(msg["fig"], width="stretch", key=f"aihub_chart_{idx}")
            if msg.get("data") is not None:
                st.dataframe(msg["data"], width="stretch", key=f"aihub_data_{idx}")
            if msg.get("code"):
                with st.expander("💻 View Generated Python Code", expanded=False):
                    st.code(msg["code"], language="python")

    user_query = st.chat_input("Ask Copilot a question (e.g. 'Who are top 5 clients by sales?', 'Flag outliers in profit')...")
    prompt_to_run = clicked_prompt or user_query

    if prompt_to_run:
        st.session_state.copilot_messages.append({"role": "user", "content": prompt_to_run})
        copilot_res = ask_data_copilot(working_df, prompt_to_run, api_key=user_llm_key if 'user_llm_key' in locals() and user_llm_key else None)
        st.session_state.copilot_messages.append({
            "role": "assistant",
            "content": copilot_res["answer"],
            "data": copilot_res.get("data"),
            "fig": copilot_res.get("fig"),
            "code": copilot_res.get("generated_code")
        })
        st.rerun()


# ==============================================================
# TAB 2: CODE INTERPRETER SANDBOX
# ==============================================================
with tab_sandbox:
    st.markdown("##### 🧪 Python Code Interpreter (Isolated Execution)")
    st.caption("Write and execute custom Pandas and Plotly code directly against `df`. Assign `result = df...` or `fig = px...` to render interactive outputs.")

    default_code = (
        "# Dynamic Pandas & Plotly Script\n"
        "num_cols = df.select_dtypes(include=['number']).columns\n"
        "if len(num_cols) > 0:\n"
        "    col = num_cols[0]\n"
        "    result = df.describe().T[['mean', 'std', 'min', '50%', 'max']]\n"
        "    fig = px.histogram(df, x=col, title=f'Distribution of {col}', nbins=25)\n"
        "    fig.update_layout(template='plotly_dark')\n"
        "else:\n"
        "    result = df.head(10)\n"
    )

    code_input = st.text_area("Python Script", value=default_code, height=160, key="aihub_sandbox_code")

    if st.button("⚡ Run in Sandbox", type="primary", key="btn_run_aihub_sandbox"):
        exec_res = run_sandboxed_pandas_code(working_df, code_input)
        if exec_res["error"]:
            st.error(f"Execution Error: {exec_res['error']}")
        else:
            st.success("Execution completed successfully!")
            if exec_res["stdout"]:
                with st.expander("📜 Standard Output (Console)", expanded=True):
                    st.text(exec_res["stdout"])
            if exec_res["fig"] is not None:
                st.plotly_chart(exec_res["fig"], width="stretch", key="aihub_sandbox_fig")
            if exec_res["data"] is not None:
                st.dataframe(exec_res["data"], width="stretch", key="aihub_sandbox_df")


# ==============================================================
# TAB 3: 1-CLICK AUTONOMOUS AUTO-PILOT
# ==============================================================
with tab_autopilot:
    st.markdown("##### 🚀 1-Click Autonomous Auto-Pilot Audit")
    st.caption("Let the autonomous agent diagnose your dataset, determine the commercial/scientific domain, clean data, compute KPIs, and build visual summaries in seconds.")

    if st.button("⚡ Execute 1-Click Autonomous Audit", type="primary", key="btn_run_autopilot_hub"):
        with st.spinner("Analyzing dataset patterns..."):
            st.session_state.autopilot_result = run_autonomous_audit(working_df, st.session_state.dataset_name)
            save_checkpoint(st.session_state.project_id, "Autonomous Auto-Pilot", working_df, "1-Click Autonomous Audit Execution")
            st.session_state.last_action_msg = "Autonomous 1-Click Audit completed!"
            st.rerun()

    if st.session_state.autopilot_result:
        ap_res = st.session_state.autopilot_result
        st.markdown(f"""
        <div class="plain-box">
            <span class="plain-badge">AUTONOMOUS AUDIT [{ap_res['domain_tag'].upper()}]</span>
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

        c1, c2 = st.columns(2)
        with c1:
            if "cat_bar" in ap_res.get("exec_charts", {}):
                st.plotly_chart(ap_res["exec_charts"]["cat_bar"], width="stretch", key="aihub_ap_cat")
        with c2:
            if ap_res.get("waterfall_fig"):
                st.plotly_chart(ap_res["waterfall_fig"], width="stretch", key="aihub_ap_wf")
            elif "trend" in ap_res.get("exec_charts", {}):
                st.plotly_chart(ap_res["exec_charts"]["trend"], width="stretch", key="aihub_ap_trend")


# ==============================================================
# TAB 4: PREDICTIVE AUTOML ENGINE
# ==============================================================
with tab_automl:
    st.markdown("##### 🤖 Automated Predictive Machine Learning (AutoML)")
    st.caption("Benchmark multiple classification or regression algorithms with automated 5-fold cross-validation and feature importance analysis.")

    all_cols = working_df.columns.tolist()
    target_cand = all_cols[-1]
    for c in all_cols:
        if any(k in c.lower() for k in ["churn", "target", "status", "price", "diagnosis", "medhouseval"]):
            target_cand = c
            break

    target_sel = st.selectbox("Predictive Target Column", all_cols, index=all_cols.index(target_cand), key="aihub_target_sel")
    inferred_task = detect_task_type(working_df, target_sel)
    st.info(f"💡 Auto-Inferred Machine Learning Task: **{inferred_task.upper()}** for target `{target_sel}`")

    if st.button("🚀 Train & Benchmark Models", type="primary", key="btn_train_aihub_models"):
        with st.spinner(f"Training cross-validated {inferred_task} pipelines..."):
            try:
                X, y, task_t, target_enc, feat_encs = prepare_ml_data(working_df, target_sel)
                res_df, models, best_m, diag_m, feat_imp, test_score = train_and_evaluate_models(X, y, task_t)
                st.session_state.trained_ml = {
                    "results_df": res_df,
                    "target_col": target_sel,
                    "task_type": task_t,
                    "best_model_name": best_m,
                    "best_model_obj": models.get(best_m),
                    "diag_metrics": diag_m,
                    "feat_importances": feat_imp,
                    "test_score": test_score
                }
                save_checkpoint(st.session_state.project_id, "AutoML Training", working_df, f"Trained ML models on {target_sel}")
                st.session_state.last_action_msg = f"Trained models successfully! Best algorithm: {best_m}"
                st.rerun()
            except Exception as e:
                st.error(f"AutoML training error: {e}")

    if st.session_state.get("trained_ml"):
        ml_data = st.session_state.trained_ml
        st.markdown(f"##### 🏆 Model Leaderboard (Target: `{ml_data['target_col']}`)")
        st.dataframe(ml_data["results_df"], width="stretch", hide_index=True)

        if ml_data.get("feat_importances") is not None and not ml_data["feat_importances"].empty:
            st.markdown("##### 🔍 Feature Importance Ranking")
            import plotly.express as px
            fig_imp = px.bar(
                ml_data["feat_importances"].head(10),
                x="Importance",
                y="Feature",
                orientation="h",
                title="Top Predictive Features",
                color="Importance",
                color_continuous_scale="Purples"
            )
            fig_imp.update_layout(template="plotly_dark", yaxis=dict(autorange="reversed"))
            st.plotly_chart(fig_imp, width="stretch", key="aihub_feat_imp_plot")

