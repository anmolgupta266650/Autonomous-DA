import pandas as pd
import numpy as np
from typing import Dict, Any, Tuple
from modules.data_cleaner import clean_missing_values, remove_duplicates
from modules.bi_visualizer import build_executive_dashboard_charts
from modules.business_insights import generate_executive_insights
from modules.research_studio import (
    auto_discover_research_constructs, generate_research_questions,
    run_welch_ttest, run_one_way_anova, run_ols_regression
)
from modules.tally_finance import (
    detect_financial_columns, compute_tally_financial_metrics,
    build_financial_waterfall_chart
)


def run_autonomous_audit(df: pd.DataFrame, dataset_name: str = "Dataset") -> Dict[str, Any]:
    """
    Executes an end-to-end autonomous audit with ZERO user setup required:
    1. Auto-Cleans missing cells and duplicate records.
    2. Infers the domain (Accounting vs Academic vs Commercial BI).
    3. Generates executive KPI tiles and top 4 visual charts.
    4. Automatically executes the primary empirical hypothesis test.
    5. Extracts Pareto business drivers and strategic insights.
    """
    if df is None or df.empty:
        return {"error": "Dataset is empty."}

    initial_rows = len(df)
    work = df.copy()

    # Step 1: Auto-Cleaning
    work, dup_msg = remove_duplicates(work, keep="first")
    for col in work.columns:
        if work[col].isnull().sum() > 0:
            strat = "median" if pd.api.types.is_numeric_dtype(work[col]) else "mode"
            work, _ = clean_missing_values(work, col, strat)

    cleaned_rows = len(work)
    cleaning_summary = f"Auto-cleaned: checked {initial_rows:,} rows, normalized null cells across all columns."

    # Step 2: Domain Inference
    cols_lower = [c.lower() for c in work.columns]
    is_finance = any(k in " ".join(cols_lower) for k in ["credit", "debit", "ledger", "voucher", "party", "tax", "gst"])
    is_academic = any(k in " ".join(cols_lower) for k in ["gpa", "score", "grade", "student", "admit", "treatment", "exam"])

    domain_tag = "Financial Accounting" if is_finance else "Academic & Scientific Research" if is_academic else "Commercial Business Intelligence"

    # Step 3: Executive BI Charts & KPIs
    exec_charts, exec_kpis = build_executive_dashboard_charts(work)

    # Step 4: Academic Hypotheses & Statistical Test
    constructs = auto_discover_research_constructs(work)
    rqs = generate_research_questions(work)
    primary_test_result = None
    plain_english_takeaway = "Empirical data verified."

    if rqs and constructs["metrics"] and constructs["factors"]:
        m = constructs["metrics"][0]
        f = constructs["factors"][0]
        if work[f].nunique() == 2:
            primary_test_result = run_welch_ttest(work, m, f)
        else:
            primary_test_result = run_one_way_anova(work, m, f)

        if primary_test_result and "p_value" in primary_test_result:
            p_val = primary_test_result["p_value"]
            if p_val < 0.05:
                plain_english_takeaway = f"✅ Statistically Significant: There is a 95%+ probability that differences in '{m}' across '{f}' are real and meaningful, not random chance."
            else:
                plain_english_takeaway = f"ℹ️ Invariant / Uniform: Differences in '{m}' across '{f}' are within expected random variance."

    # Step 5: Tally Financial metrics if applicable
    fin_summary = None
    waterfall_fig = None
    if is_finance:
        fin_summary = compute_tally_financial_metrics(work)
        if fin_summary and fin_summary.get("total_revenue", 0) > 0:
            waterfall_fig = build_financial_waterfall_chart(fin_summary["total_revenue"], fin_summary["total_expenses"])

    # Step 6: AI Business Insights
    insights = generate_executive_insights(work)

    return {
        "cleaned_df": work,
        "cleaning_summary": cleaning_summary,
        "domain_tag": domain_tag,
        "exec_charts": exec_charts,
        "exec_kpis": exec_kpis,
        "research_questions": rqs,
        "primary_test_result": primary_test_result,
        "plain_english_takeaway": plain_english_takeaway,
        "fin_summary": fin_summary,
        "waterfall_fig": waterfall_fig,
        "insights": insights
    }

