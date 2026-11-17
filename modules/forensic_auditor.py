import numpy as np
import pandas as pd
import scipy.stats as stats
import plotly.graph_objects as go
from typing import Dict, Any, Tuple, List, Optional


def run_benfords_law_analysis(df: pd.DataFrame, amount_col: str) -> Tuple[Dict[str, Any], go.Figure]:
    """
    Executes Benford's Law Forensic Audit on transaction amounts.
    Detects manipulated or fabricated invoice/voucher numbers.
    """
    if df is None or df.empty or not amount_col or amount_col not in df.columns:
        return {"error": "Invalid or missing amount column for forensic audit."}, go.Figure()

    clean_series = pd.to_numeric(df[amount_col].astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce").dropna()
    clean_series = clean_series[clean_series > 0]

    if len(clean_series) < 30:
        return {"error": "Requires at least 30 positive numeric transactions for Benford's Law analysis."}, go.Figure()

    # Extract first leading digit
    first_digits = clean_series.astype(str).str.lstrip("0.").str[0].astype(int)
    first_digits = first_digits[(first_digits >= 1) & (first_digits <= 9)]

    total_count = len(first_digits)
    observed_counts = first_digits.value_counts().reindex(range(1, 10), fill_value=0)
    observed_pct = (observed_counts / total_count * 100).round(2)

    # Benford's theoretical probability: P(d) = log10(1 + 1/d)
    benford_probs = np.array([np.log10(1 + 1 / d) for d in range(1, 10)])
    benford_probs = benford_probs / benford_probs.sum()
    benford_pct = (benford_probs * 100).round(2)
    benford_counts = benford_probs * total_count

    # Chi-Square Goodness of Fit Test
    chi2_stat, p_val = stats.chisquare(f_obs=observed_counts.values, f_exp=benford_counts)

    is_anomalous = p_val < 0.05
    max_deviation_digit = int(np.argmax(np.abs(observed_pct.values - benford_pct)) + 1)
    max_dev_pct = float(abs(observed_pct.iloc[max_deviation_digit - 1] - benford_pct[max_deviation_digit - 1]))

    # Chart
    fig = go.Figure()
    fig.add_trace(go.Bar(
        x=[f"Digit {d}" for d in range(1, 10)],
        y=observed_pct.values,
        name="Observed Actual %",
        marker=dict(color="#3b82f6", line=dict(color="#1d4ed8", width=1.5)),
        opacity=0.85
    ))
    fig.add_trace(go.Scatter(
        x=[f"Digit {d}" for d in range(1, 10)],
        y=benford_pct,
        name="Benford's Expected %",
        mode="lines+markers",
        line=dict(color="#ef4444", width=3, dash="dash"),
        marker=dict(size=8, color="#dc2626")
    ))

    fig.update_layout(
        title="<b>Benford's Law Forensic Digit Analysis (Invoice Fabrication Audit)</b>",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc", family="Inter, sans-serif"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        height=380,
        margin=dict(l=40, r=40, t=60, b=40)
    )

    result_summary = {
        "total_audited": total_count,
        "chi2_statistic": float(chi2_stat),
        "p_value": float(p_val),
        "is_anomalous": is_anomalous,
        "max_deviation_digit": max_deviation_digit,
        "max_dev_pct": max_dev_pct,
        "verdict": "⚠️ High Conformity Deviation: Potential manual manipulation or artificial invoice capping detected." if is_anomalous else "✅ Normal Conformity: Leading digits align with standard natural financial distributions."
    }
    return result_summary, fig


def detect_duplicate_transactions(df: pd.DataFrame, party_col: str, amount_col: str, date_col: Optional[str] = None) -> pd.DataFrame:
    """
    Identifies potential duplicate invoices or disbursements (same party, identical amount).
    """
    if df is None or df.empty or not party_col or party_col not in df.columns or not amount_col or amount_col not in df.columns:
        return pd.DataFrame()

    work = df[[party_col, amount_col] + ([date_col] if date_col and date_col in df.columns else [])].dropna().copy()
    work[amount_col] = pd.to_numeric(work[amount_col].astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce")
    work = work.dropna(subset=[amount_col])

    # Find duplicates
    subset_cols = [party_col, amount_col]
    dups = work[work.duplicated(subset=subset_cols, keep=False)].sort_values(by=subset_cols)

    return dups


def detect_round_number_spikes(df: pd.DataFrame, amount_col: str) -> Dict[str, Any]:
    """
    Flags unusual concentrations of round numbers (e.g. ₹10,000, ₹50,000, ₹1,00,000).
    Often associated with unapproved petty cash withdrawals or estimated lump-sum invoices.
    """
    if df is None or df.empty or not amount_col or amount_col not in df.columns:
        return {}

    amounts = pd.to_numeric(df[amount_col].astype(str).str.replace(r"[^0-9.]", "", regex=True), errors="coerce").dropna()
    amounts = amounts[amounts > 0]

    if len(amounts) == 0:
        return {}

    round_thousands = amounts[amounts % 1000 == 0]
    round_ten_thousands = amounts[amounts % 10000 == 0]

    pct_thousands = (len(round_thousands) / len(amounts) * 100)
    pct_ten_thousands = (len(round_ten_thousands) / len(amounts) * 100)

    is_abnormal = pct_thousands > 30.0

    return {
        "total_transactions": len(amounts),
        "round_thousands_count": len(round_thousands),
        "round_thousands_pct": round(pct_thousands, 1),
        "round_ten_thousands_count": len(round_ten_thousands),
        "round_ten_thousands_pct": round(pct_ten_thousands, 1),
        "is_abnormal": is_abnormal,
        "warning": "⚠️ High concentration of exact round sums detected (>30% of total transactions)." if is_abnormal else "✅ Natural amount variance observed."
    }
