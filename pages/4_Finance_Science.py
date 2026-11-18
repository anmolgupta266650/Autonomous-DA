import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from modules.common_ui import render_sidebar_data_controls, render_page_header
from modules.tally_finance import (
    detect_financial_columns, compute_tally_financial_metrics,
    build_financial_waterfall_chart, build_debtor_aging_analysis,
    get_plain_english_financial_summary
)
from modules.forensic_auditor import (
    run_benfords_law_analysis, detect_duplicate_transactions,
    detect_round_number_spikes
)
from modules.research_studio import (
    auto_discover_research_constructs, generate_research_questions,
    run_welch_ttest, run_one_way_anova, run_ols_regression,
    generate_apa_research_paper, get_plain_english_interpretation
)
from modules.data_loader import get_dataset_metadata
from modules.db_manager import save_checkpoint, save_research_paper

working_df = render_sidebar_data_controls()
render_page_header("💼 Finance & Science Studios", working_df)

meta = get_dataset_metadata(working_df)

st.markdown("### 💼 Specialized Finance & Scientific Research Studios")
st.caption("P&L statements, corporate debtor aging, forensic Benford's Law auditing, interactive What-If sensitivity forecasting, and empirical APA research papers.")

tab_tally, tab_audit, tab_whatif, tab_science = st.tabs([
    "💼 Tally Financial Statements & P&L",
    "🕵️ Forensic Audit & Fraud Detection",
    "🎯 What-If Scenario Simulator",
    "🔬 Academic & Scientific Research"
])

auto_fin = detect_financial_columns(working_df)

# ==============================================================
# TAB 1: TALLY FINANCIAL STATEMENTS
# ==============================================================
with tab_tally:
    st.markdown("##### 💼 Corporate P&L & Cash Flow Performance")
    tf_c1, tf_c2, tf_c3, tf_c4 = st.columns(4)
    with tf_c1:
        rev_f = st.selectbox("Revenue / Credit Column", ["Auto-Detect"] + working_df.columns.tolist(), key="fin_rev_sel")
    with tf_c2:
        exp_f = st.selectbox("Cost / Debit Column", ["Auto-Detect", "None (Use 70% Benchmark)"] + working_df.columns.tolist(), key="fin_exp_sel")
    with tf_c3:
        party_f = st.selectbox("Party / Debtor Column", ["Auto-Detect"] + working_df.columns.tolist(), key="fin_party_sel")
    with tf_c4:
        date_f = st.selectbox("Transaction Date Column", ["Auto-Detect"] + working_df.columns.tolist(), key="fin_date_sel")

    act_rev = auto_fin["revenue"] if rev_f == "Auto-Detect" else rev_f
    act_exp = None if exp_f == "None (Use 70% Benchmark)" else (auto_fin["expense"] if exp_f == "Auto-Detect" else exp_f)
    act_party = auto_fin["party"] if party_f == "Auto-Detect" else party_f
    act_date = auto_fin["date"] if date_f == "Auto-Detect" else date_f

    fin_metrics = compute_tally_financial_metrics(working_df, rev_col=act_rev, exp_col=act_exp, date_col=act_date, party_col=act_party)

    if fin_metrics:
        plain_fin = get_plain_english_financial_summary(fin_metrics)
        st.markdown(f"""
        <div class="plain-box">
            <span class="plain-badge">EXECUTIVE FINANCIAL HEALTH</span>
            <h4 style="margin: 4px 0 6px 0; color: #f8fafc;">{plain_fin['title']}</h4>
            <p style="margin: 0; color: #cbd5e1; font-size: 0.92rem;">{plain_fin['takeaway']}</p>
        </div>
        """, unsafe_allow_html=True)

        tk1, tk2, tk3, tk4 = st.columns(4)
        with tk1:
            st.metric("Total Turnover", f"₹{fin_metrics['total_revenue']:,.0f}")
        with tk2:
            st.metric("Operating Costs", f"₹{fin_metrics['total_expenses']:,.0f}")
        with tk3:
            st.metric("Gross Profit", f"₹{fin_metrics['gross_profit']:,.0f}")
        with tk4:
            st.metric("Profit Margin", f"{fin_metrics['gross_margin']:.1f}%")

        st.write("")
        wf_chart = build_financial_waterfall_chart(fin_metrics['total_revenue'], fin_metrics['total_expenses'])
        st.plotly_chart(wf_chart, width="stretch", key="finstudio_waterfall")

        if act_party and act_date and act_rev:
            with st.expander("📊 Accounts Receivable Debtor Aging Analysis", expanded=False):
                aging_df, aging_fig = build_debtor_aging_analysis(working_df, party_col=act_party, date_col=act_date, amount_col=act_rev)
                if aging_fig:
                    st.plotly_chart(aging_fig, width="stretch", key="finstudio_aging_plot")
                if not aging_df.empty:
                    st.dataframe(aging_df, width="stretch")


# ==============================================================
# TAB 2: FORENSIC AUDIT & FRAUD DETECTION
# ==============================================================
with tab_audit:
    st.markdown("##### 🕵️ Forensic Auditing & Fraud Sentinel Checks")
    st.caption("Inspect first-digit Benford's Law compliance, flag identical duplicate payments, and detect round-number petty cash clustering.")

    num_cols = meta.get("numeric_cols", [])
    amt_col = act_rev if act_rev and act_rev in working_df.columns else (num_cols[0] if num_cols else None)

    if amt_col:
        st.markdown(f"###### 1. Benford's Law Uniformity Audit (Auditing: `{amt_col}`)")
        ben_metrics, ben_fig = run_benfords_law_analysis(working_df, amt_col)
        if ben_fig:
            st.plotly_chart(ben_fig, width="stretch", key="finstudio_benford")
        if ben_metrics.get("is_anomalous"):
            st.warning(f"⚠️ {ben_metrics.get('verdict', 'Benford anomaly flagged.')}")
        else:
            st.success(f"✅ {ben_metrics.get('verdict', 'Benford distribution normal.')}")

        st.markdown("---")
        st.markdown("###### 2. Duplicate Transaction & Payment Voucher Detection")
        if act_party:
            dups = detect_duplicate_transactions(working_df, act_party, amt_col)
            if not dups.empty:
                st.warning(f"⚠️ Found **{len(dups):,} duplicate transactions** with identical party and amount!")
                st.dataframe(dups.head(20), width="stretch")
            else:
                st.success("✅ Zero identical duplicate vouchers detected.")

        st.markdown("---")
        st.markdown("###### 3. Round-Number Spikes (Petty Cash Clustering)")
        round_res = detect_round_number_spikes(working_df, amt_col)
        if round_res:
            st.write(f"Round Multiples of 1,000: **{round_res.get('round_thousands_pct', 0)}%** | Multiples of 10,000: **{round_res.get('round_ten_thousands_pct', 0)}%**")
            if round_res.get("is_abnormal"):
                st.warning(round_res.get("warning"))
            else:
                st.success(round_res.get("warning"))

        st.markdown("---")
        st.markdown("###### 🚨 Automated Forensic Sentinel Incident Digest")
        dup_count = len(dups) if (act_party and 'dups' in locals() and not dups.empty) else 0
        is_benford_bad = ben_metrics.get("is_anomalous", False)
        is_round_bad = round_res.get("is_abnormal", False) if round_res else False

        total_anomalies = (1 if is_benford_bad else 0) + (1 if dup_count > 0 else 0) + (1 if is_round_bad else 0)
        risk_level = "CRITICAL" if total_anomalies >= 2 else ("ELEVATED" if total_anomalies == 1 else "LOW RISK")
        risk_color = "#ef4444" if total_anomalies >= 2 else ("#f59e0b" if total_anomalies == 1 else "#10b981")

        st.markdown(
            f'<div style="background: rgba(15, 23, 42, 0.85); border: 1px solid {risk_color}55; border-left: 4px solid {risk_color}; border-radius: 8px; padding: 14px 18px; margin: 10px 0;">'
            f'<div style="display: flex; justify-content: space-between; align-items: center;">'
            f'<div><span style="font-size: 0.75rem; text-transform: uppercase; font-weight: 700; color: #94a3b8;">COMPOSITE SENTINEL RISK SCORE</span>'
            f'<div style="font-size: 1.25rem; font-weight: 800; color: {risk_color};">{risk_level} — {total_anomalies} Anomaly Categories Flagged</div></div>'
            f'<div style="background: {risk_color}22; color: {risk_color}; font-weight: 700; padding: 4px 12px; border-radius: 9999px; font-size: 0.8rem;">Audit Verified</div>'
            f'</div>'
            f'</div>',
            unsafe_allow_html=True
        )

        incident_report = (
            f"AUTONOMOUS DA ENTERPRISE — FORENSIC SENTINEL INCIDENT REPORT\n"
            f"Generated: {pd.Timestamp.now().strftime('%Y-%m-%d %H:%M:%S UTC')}\n"
            f"Audited Dataset: {st.session_state.dataset_name}\n"
            f"Composite Risk Rating: {risk_level}\n\n"
            f"1. Benford's Law Chi-Square Audit: {'ANOMALOUS SPIKE DETECTED' if is_benford_bad else 'COMPLIANT'}\n"
            f"   Detail: {ben_metrics.get('verdict', 'N/A')}\n\n"
            f"2. Duplicate Vouchers: {dup_count} duplicate disbursements identified.\n\n"
            f"3. Round-Number Clustering: {'ABNORMAL SPIKE' if is_round_bad else 'NORMAL DISPERSION'}\n"
            f"   Detail: {round_res.get('warning', 'N/A') if round_res else 'N/A'}\n"
        )
        st.download_button(
            "📥 Download Executive Incident Briefing (.txt)",
            data=incident_report,
            file_name=f"Forensic_Incident_Report_{st.session_state.project_id}.txt",
            mime="text/plain",
            key="btn_dl_incident_rep"
        )
    else:
        st.info("No numerical transaction amount column available for forensic auditing.")


# ==============================================================
# TAB 3: WHAT-IF SCENARIO SIMULATION
# ==============================================================
with tab_whatif:
    st.markdown("##### 🎯 Executive What-If Sensitivity Simulator")
    st.caption("Stress test your business: adjust volume, pricing power, supplier inflation, and tax rates to project impact on bottom-line profit.")

    base_rev = float(fin_metrics['total_revenue']) if (fin_metrics and fin_metrics.get('total_revenue', 0) > 0) else 1000000.0
    base_exp = float(fin_metrics['total_expenses']) if (fin_metrics and fin_metrics.get('total_expenses', 0) > 0) else base_rev * 0.70
    base_profit = base_rev - base_exp
    base_margin = (base_profit / base_rev * 100.0) if base_rev > 0 else 0.0

    sc1, sc2, sc3, sc4 = st.columns(4)
    with sc1:
        price_shift = st.slider("Price Shift (%)", -30, 50, 0, step=1, key="finstudio_p_shift")
    with sc2:
        vol_shift = st.slider("Volume Shift (%)", -30, 50, 0, step=1, key="finstudio_v_shift")
    with sc3:
        cost_shift = st.slider("Cost Inflation (%)", -20, 50, 0, step=1, key="finstudio_c_shift")
    with sc4:
        tax_rate = st.slider("Tax / Overhead (%)", 0, 40, 15, step=1, key="finstudio_tax_rate")

    proj_rev = base_rev * (1.0 + vol_shift / 100.0) * (1.0 + price_shift / 100.0)
    proj_exp = base_exp * (1.0 + vol_shift / 100.0) * (1.0 + cost_shift / 100.0)
    proj_ebitda = proj_rev - proj_exp
    proj_tax = max(0.0, proj_ebitda * (tax_rate / 100.0))
    proj_net = proj_ebitda - proj_tax
    proj_margin = (proj_net / proj_rev * 100.0) if proj_rev > 0 else 0.0
    delta_profit = proj_net - base_profit

    st.write("")
    wk1, wk2, wk3, wk4 = st.columns(4)
    wk1.metric("Projected Revenue", f"₹{proj_rev:,.0f}", f"{(proj_rev - base_rev):+,.0f}")
    wk2.metric("Projected Expenses", f"₹{proj_exp:,.0f}", f"{(proj_exp - base_exp):+,.0f}", delta_color="inverse")
    wk3.metric("Projected Net Profit", f"₹{proj_net:,.0f}", f"{delta_profit:+,.0f}")
    wk4.metric("Simulated Margin", f"{proj_margin:.1f}%", f"{(proj_margin - base_margin):+.1f}%")

    wf_fig = go.Figure(go.Waterfall(
        name="Sensitivity Projection",
        orientation="v",
        measure=["absolute", "relative", "relative", "total", "relative", "relative", "total"],
        x=["Baseline Revenue", "Volume Effect", "Price Effect", "Projected Turnover", "Cost Impact", "Tax / Overhead", "Projected Net"],
        textposition="outside",
        y=[
            base_rev,
            base_rev * (vol_shift / 100.0),
            proj_rev - (base_rev * (1.0 + vol_shift / 100.0)),
            proj_rev,
            -proj_exp,
            -proj_tax,
            proj_net
        ],
        connector={"line": {"color": "#6366f1"}},
        decreasing={"marker": {"color": "#ef4444"}},
        increasing={"marker": {"color": "#10b981"}},
        totals={"marker": {"color": "#06b6d4"}}
    ))
    wf_fig.update_layout(title="<b>Projected Financial Waterfall Under Simulated Conditions</b>", template="plotly_dark", height=420)
    st.plotly_chart(wf_fig, width="stretch", key="finstudio_whatif_wf")


# ==============================================================
# TAB 4: ACADEMIC & SCIENTIFIC RESEARCH
# ==============================================================
with tab_science:
    st.markdown("##### 🔬 Academic & Scientific Empirical Research Studio")
    st.caption("Formulate testable research questions, compute Welch's t-tests, ANOVA, OLS regressions, and auto-draft APA 7th Edition manuscripts.")

    rqs = generate_research_questions(working_df)
    if rqs:
        st.markdown(f"###### 🧪 Auto-Discovered Hypotheses ({len(rqs)} Formulated)")
        for rq in rqs:
            st.markdown(f"**[{rq['id']}] {rq['question']}**\n- *{rq['null_hypothesis']}*\n- *{rq['alt_hypothesis']}*")

        st.markdown("---")
        sci_c1, sci_c2 = st.columns(2)
        with sci_c1:
            cat_cols = meta.get("categorical_cols", [])
            num_cols = meta.get("numeric_cols", [])
            grp_col = st.selectbox("Group Dimension (IV)", cat_cols, key="sci_grp_sel") if cat_cols else None
            val_col = st.selectbox("Continuous Metric (DV)", num_cols, key="sci_val_sel") if num_cols else None

        with sci_c2:
            stat_test = st.selectbox("Statistical Procedure", ["Welch's Two-Sample t-test", "One-Way ANOVA", "OLS Regression"], key="sci_proc_sel")

        if st.button("⚡ Execute Statistical Test & Synthesize Paper", type="primary", key="btn_run_stat_test"):
            if grp_col and val_col:
                if "t-test" in stat_test:
                    test_res = run_welch_ttest(working_df, val_col, grp_col)
                elif "ANOVA" in stat_test:
                    test_res = run_one_way_anova(working_df, val_col, grp_col)
                else:
                    preds = [c for c in num_cols if c != val_col][:3]
                    test_res = run_ols_regression(working_df, val_col, preds)

                if "error" in test_res:
                    st.error(test_res["error"])
                else:
                    st.success(f"Test Completed! Plain-English Takeaway: {get_plain_english_interpretation(test_res)}")
                    paper_md = generate_apa_research_paper(working_df, st.session_state.dataset_name, rqs, test_res)
                    st.session_state.active_research_paper = paper_md
                    save_research_paper(st.session_state.project_id, f"APA Paper: {val_col}", paper_md)
                    st.session_state.last_action_msg = "Synthesized APA 7th Edition Research Paper!"
                    st.rerun()

    if st.session_state.get("active_research_paper"):
        st.markdown("##### 📝 Synthesized APA 7th Edition Manuscript Preview")
        st.download_button(
            "⬇️ Download Full APA Manuscript (.md)",
            data=st.session_state.active_research_paper,
            file_name="Research_Paper_APA7.md",
            mime="text/markdown",
            key="btn_dl_science_paper"
        )
        with st.expander("📄 View Manuscript", expanded=True):
            st.markdown(st.session_state.active_research_paper)

