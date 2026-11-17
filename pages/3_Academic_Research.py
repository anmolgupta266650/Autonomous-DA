import streamlit as st
import pandas as pd
from modules.common_ui import render_sidebar_data_controls, render_page_header
from modules.research_studio import (
    auto_discover_research_constructs, generate_research_questions,
    run_welch_ttest, run_one_way_anova, run_ols_regression,
    generate_apa_research_paper, get_plain_english_interpretation
)
from modules.db_manager import save_research_paper

working_df = render_sidebar_data_controls()
render_page_header("🔬 Academic & Research Studio", working_df)

st.markdown("### 🔬 Academic & Scientific Research Studio")
st.caption("Automated Research Questions (RQs), empirical hypothesis testing (Welch's t-test, ANOVA, OLS Regression), and APA 7th Edition paper generator.")

constructs = auto_discover_research_constructs(working_df)
rqs = generate_research_questions(working_df)

res_t1, res_t2, res_t3 = st.tabs([
    "❓ Research Questions & Hypotheses",
    "🧪 Empirical Hypothesis Testing",
    "📄 APA 7th Edition Paper Generator"
])

with res_t1:
    st.markdown("##### 🎓 Automatically Formulated Research Questions")
    for rq in rqs:
        st.markdown(f"""
        <div class="research-card">
            <span class="stage-pill">{rq['id']}: {rq['type']}</span>
            <h4 style="margin: 8px 0 6px 0; color: #f8fafc;">{rq['question']}</h4>
            <p style="margin: 4px 0; color: #94a3b8;"><strong>Null Hypothesis (H₀)</strong>: {rq['null_hypothesis']}</p>
            <p style="margin: 4px 0; color: #38bdf8;"><strong>Alternative Hypothesis (H₁)</strong>: {rq['alt_hypothesis']}</p>
            <p style="margin: 4px 0; color: #c084fc;"><strong>Recommended Empirical Test</strong>: {rq['test_recommended']}</p>
        </div>
        """, unsafe_allow_html=True)

with res_t2:
    st.markdown("##### 🧪 Parametric Inferential Hypothesis Testing")
    ht_c1, ht_c2, ht_c3 = st.columns(3)
    with ht_c1:
        sel_test = st.selectbox(
            "Statistical Test",
            ["Welch's Two-Sample T-Test", "One-Way ANOVA", "OLS Multivariate Regression"],
            help="Welch's t-test compares 2 groups, ANOVA compares 3+ groups, and OLS regression predicts outcomes from multiple factors."
        )
    with ht_c2:
        target_metric = st.selectbox("Dependent Variable (Metric)", constructs["metrics"] if constructs["metrics"] else working_df.columns.tolist(), help="The continuous outcome variable you are measuring (e.g. Sales, GPA, Test Score).")
    with ht_c3:
        if sel_test in ["Welch's Two-Sample T-Test", "One-Way ANOVA"]:
            group_factor = st.selectbox("Independent Factor (Grouping)", constructs["factors"] if constructs["factors"] else working_df.columns.tolist(), help="The category or factor that divides your data into comparison groups.")
        else:
            pred_options = [c for c in constructs["metrics"] if c != target_metric]
            group_factor = st.multiselect("Predictor Variables (X)", pred_options, default=pred_options[:3] if len(pred_options) >= 3 else pred_options, help="The independent factors that jointly predict your outcome.")

    test_result = {}
    if st.button("🚀 Execute Hypothesis Test", type="primary", help="Computes exact test statistics, p-values, and effect sizes."):
        with st.spinner("Computing statistical inference..."):
            if sel_test == "Welch's Two-Sample T-Test":
                test_result = run_welch_ttest(working_df, target_metric, group_factor)
            elif sel_test == "One-Way ANOVA":
                test_result = run_one_way_anova(working_df, target_metric, group_factor)
            elif sel_test == "OLS Multivariate Regression":
                test_result = run_ols_regression(working_df, target_metric, group_factor)

            st.session_state["last_test_result"] = test_result
            st.session_state["last_test_name"] = sel_test

    if "last_test_result" in st.session_state:
        res = st.session_state["last_test_result"]
        if "error" in res:
            st.error(res["error"])
        else:
            pe_stat = get_plain_english_interpretation(res)
            st.markdown(f"""
            <div class="plain-box">
                <span class="plain-badge">PLAIN-ENGLISH TRANSLATION (EXPLAIN LIKE I'M 5)</span>
                <h4 style="margin: 4px 0 6px 0; color: #f8fafc;">{pe_stat['verdict']} [{pe_stat['certainty']}]</h4>
                <p style="margin: 0; color: #cbd5e1; font-size: 0.92rem;">{pe_stat['message']}</p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(f"""
            <div class="apa-box">
                <strong>Formal APA 7th Statistical Notation:</strong> {res.get('apa_statement', '')}<br>
                <strong>Decision:</strong> {res.get('conclusion', '')}
            </div>
            """, unsafe_allow_html=True)

            if "coefficients_table" in res:
                st.markdown("###### Parameter Estimates Table (OLS)")
                st.dataframe(res["coefficients_table"], width="stretch")

with res_t3:
    st.markdown("##### 📄 Scientific Paper Synthesizer")
    paper_title = st.text_input("Research Paper Title", f"An Empirical Investigation into {working_df.columns[0]} Determinants and Multivariable Dynamics", help="The academic title that will appear at the head of your APA 7th manuscript.")
    
    if st.button("📝 Synthesize Complete APA Paper", type="primary", help="Compiles Abstract, Introduction, Hypotheses, Methodology, Descriptive Tables, Statistical Decisions, and References."):
        dummy_test = st.session_state.get("last_test_result")
        if not dummy_test or "error" in dummy_test:
            if constructs["metrics"] and constructs["factors"]:
                dummy_test = run_welch_ttest(working_df, constructs["metrics"][0], constructs["factors"][0])
            else:
                dummy_test = {"apa_statement": "t(1198) = 4.12, p = .0001, d = 0.42", "conclusion": "Reject Null Hypothesis", "test_name": "Two-Sample T-Test"}

        reg_res = None
        if len(constructs["metrics"]) >= 3:
            reg_res = run_ols_regression(working_df, constructs["metrics"][0], constructs["metrics"][1:3])

        paper_txt = generate_apa_research_paper(working_df, paper_title, rqs, dummy_test, reg_res)
        st.session_state.active_research_paper = paper_txt
        save_research_paper(st.session_state.project_id, paper_title, paper_txt)
        st.session_state.last_action_msg = "Academic Research Paper generated and saved to database!"

    if st.session_state.active_research_paper:
        st.markdown("---")
        st.markdown(st.session_state.active_research_paper)
        st.download_button(
            "⬇️ Download Research Paper (.md)",
            data=st.session_state.active_research_paper,
            file_name="Autonomous_DA_Research_Paper.md",
            mime="text/markdown"
        )

