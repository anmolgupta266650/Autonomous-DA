import streamlit as st
import pandas as pd
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

working_df = render_sidebar_data_controls()
render_page_header("💼 Tally & Financial Accounting", working_df)

st.markdown("### 💼 Tally & Corporate Financial Accounting Studio")
st.caption("P&L statement analysis, financial waterfall breakdowns, accounts receivable aging, and party ledger summaries.")

auto_fin = detect_financial_columns(working_df)

tab_pl, tab_forensic = st.tabs(["📊 Financial Statements & P&L", "🕵️ Forensic Audit & Fraud Detection"])

with tab_pl:
    tf_c1, tf_c2, tf_c3, tf_c4 = st.columns(4)
    with tf_c1:
        rev_f = st.selectbox("Revenue / Credit Column", ["Auto-Detect"] + working_df.columns.tolist(), help="The column containing your gross sales, credit, or total turnover.")
    with tf_c2:
        exp_f = st.selectbox("Cost / Debit Column", ["Auto-Detect", "None (Use 70% Industry Benchmark)"] + working_df.columns.tolist(), help="The column containing direct expenses, COGS, or debits.")
    with tf_c3:
        party_f = st.selectbox("Party / Debtor Column", ["Auto-Detect"] + working_df.columns.tolist(), help="The client or vendor name column for debtor concentration.")
    with tf_c4:
        date_f = st.selectbox("Transaction Date Column", ["Auto-Detect"] + working_df.columns.tolist(), help="The transaction or invoice date column for aging buckets.")

    act_rev = auto_fin["revenue"] if rev_f == "Auto-Detect" else rev_f
    act_exp = None if exp_f == "None (Use 70% Industry Benchmark)" else (auto_fin["expense"] if exp_f == "Auto-Detect" else exp_f)
    act_party = auto_fin["party"] if party_f == "Auto-Detect" else party_f
    act_date = auto_fin["date"] if date_f == "Auto-Detect" else date_f

    fin_metrics = compute_tally_financial_metrics(working_df, rev_col=act_rev, exp_col=act_exp, date_col=act_date, party_col=act_party)

    if fin_metrics:
        plain_fin = get_plain_english_financial_summary(fin_metrics)
        st.markdown(f"""
        <div class="plain-box">
            <span class="plain-badge">PLAIN-ENGLISH EXECUTIVE FINANCIAL HEALTH</span>
            <h4 style="margin: 4px 0 6px 0; color: #f8fafc;">{plain_fin['title']}</h4>
            <p style="margin: 0; color: #cbd5e1; font-size: 0.92rem;">{plain_fin['takeaway']}</p>
        </div>
        """, unsafe_allow_html=True)

        tk1, tk2, tk3, tk4 = st.columns(4)
        with tk1:
            st.markdown(f"""
            <div class="tally-kpi">
                <div class="kpi-label">GROSS TURNOVER / REVENUE</div>
                <div class="tally-num">₹{fin_metrics['total_revenue']:,.0f}</div>
                <div class="kpi-subtext">Total Verified Inflows</div>
            </div>
            """, unsafe_allow_html=True)
        with tk2:
            st.markdown(f"""
            <div class="tally-kpi">
                <div class="kpi-label">TOTAL OPERATING EXPENSES</div>
                <div class="tally-num" style="color: #f87171;">₹{fin_metrics['total_expenses']:,.0f}</div>
                <div class="kpi-subtext">Direct Costs & COGS</div>
            </div>
            """, unsafe_allow_html=True)
        with tk3:
            st.markdown(f"""
            <div class="tally-kpi">
                <div class="kpi-label">GROSS OPERATING PROFIT</div>
                <div class="tally-num" style="color: #38bdf8;">₹{fin_metrics['gross_profit']:,.0f}</div>
                <div class="kpi-subtext">Net Retained Surplus</div>
            </div>
            """, unsafe_allow_html=True)
        with tk4:
            st.markdown(f"""
            <div class="tally-kpi">
                <div class="kpi-label">OPERATING MARGIN</div>
                <div class="tally-num" style="color: #a78bfa;">{fin_metrics['gross_margin']:.1f}%</div>
                <div class="kpi-subtext">Profitability Index</div>
            </div>
            """, unsafe_allow_html=True)

        st.write("")
        st.markdown("---")

        t_row1, t_row2 = st.columns(2)
        with t_row1:
            waterfall_fig = build_financial_waterfall_chart(fin_metrics["total_revenue"], fin_metrics["total_expenses"])
            st.plotly_chart(waterfall_fig, width="stretch", key="tally_waterfall_plot")

        with t_row2:
            if act_party and act_rev:
                aging_table, aging_fig = build_debtor_aging_analysis(working_df, act_party, act_rev, act_date)
                st.plotly_chart(aging_fig, width="stretch", key="tally_aging_plot")
            else:
                st.info("Assign a Party / Debtor and Amount column to display Accounts Receivable Aging.")

        if fin_metrics.get("top_parties"):
            st.markdown("##### 👥 Top Contributing Ledger Parties & Clients")
            st.dataframe(pd.DataFrame(fin_metrics["top_parties"]), width="stretch")
    else:
        st.warning("Please assign numeric columns to compute accounting metrics.")

with tab_forensic:
    st.markdown("#### 🕵️ Forensic Accounting & Fraud Audit Suite")
    st.caption("Apply scientific empirical rules (Benford's Law, duplicate disbursements, round number clustering) to detect accounting anomalies.")

    num_cols = working_df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = working_df.select_dtypes(include=["object", "category", "string"]).columns.tolist()

    if not num_cols:
        st.warning("Forensic analysis requires at least one numeric transaction/amount column.")
    else:
        fa_c1, fa_c2 = st.columns(2)
        with fa_c1:
            audit_amt = st.selectbox("Transaction Amount Column to Audit", num_cols, index=0)
        with fa_c2:
            audit_party = st.selectbox("Party / Vendor Column (for Duplicate Checks)", ["None"] + cat_cols, index=1 if cat_cols else 0)

        # 1. Benford's Law Test
        st.markdown("##### 1. Benford's Law Leading Digit Chi-Square Test")
        st.caption("Naturally occurring accounting numbers follow Benford's Law: $P(d) = \\log_{10}(1 + 1/d)$. Artificial limits or fabricated invoices deviate heavily.")

        benford_res, benford_fig = run_benfords_law_analysis(working_df, audit_amt)

        if "error" in benford_res:
            st.info(benford_res["error"])
        else:
            bc1, bc2, bc3, bc4 = st.columns(4)
            bc1.metric("Audited Transactions", f"{benford_res['total_audited']:,}")
            bc2.metric("Chi-Square (χ²)", f"{benford_res['chi2_statistic']:.2f}")
            bc3.metric("p-Value", f"{benford_res['p_value']:.4f}")
            bc4.metric("Max Spike Digit", f"Digit {benford_res['max_deviation_digit']} (Δ {benford_res['max_dev_pct']}%)")

            if benford_res["is_anomalous"]:
                st.error(benford_res["verdict"])
            else:
                st.success(benford_res["verdict"])

            st.plotly_chart(benford_fig, width="stretch", key="tally_benford_plot")

        st.markdown("---")

        # 2. Duplicate Payments
        st.markdown("##### 2. Duplicate Payment Voucher Detection")
        st.caption("Flags transactions where the same vendor or party received identical disbursement amounts.")
        if audit_party != "None":
            dups = detect_duplicate_transactions(working_df, audit_party, audit_amt)
            if not dups.empty:
                st.warning(f"⚠️ Found **{len(dups):,} duplicate transactions** sharing the same party and exact amount!")
                st.dataframe(dups.head(25), width="stretch")
            else:
                st.success("✅ No identical duplicate vouchers detected across the selected party and amount.")
        else:
            st.info("Select a Party / Vendor column to check for duplicate vouchers.")

        st.markdown("---")

        # 3. Round-Number Spikes
        st.markdown("##### 3. Round-Number Clustering & Petty Cash Spikes")
        st.caption("Checks for unnatural spikes in exact multiples of ₹1,000 or ₹10,000.")
        round_res = detect_round_number_spikes(working_df, audit_amt)
        if round_res:
            rc1, rc2, rc3 = st.columns(3)
            rc1.metric("Total Audited", f"{round_res.get('total_transactions', 0):,}")
            rc2.metric("Multiples of 1,000", f"{round_res.get('round_thousands_count', 0):,} ({round_res.get('round_thousands_pct', 0)}%)")
            rc3.metric("Multiples of 10,000", f"{round_res.get('round_ten_thousands_count', 0):,} ({round_res.get('round_ten_thousands_pct', 0)}%)")

            if round_res.get("is_abnormal"):
                st.warning(round_res.get("warning"))
            else:
                st.success(round_res.get("warning"))

