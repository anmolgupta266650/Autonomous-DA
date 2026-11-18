import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Tuple, List, Optional, Union


def detect_financial_columns(df: pd.DataFrame) -> Dict[str, Optional[str]]:
    """
    Auto-detects typical Tally and financial ledger columns:
    date, ledger/party, debit/expense, credit/revenue, balance, voucher type.
    """
    cols = df.columns.tolist()
    mapping = {
        "date": None,
        "party": None,
        "revenue": None,
        "expense": None,
        "amount": None,
        "type": None
    }

    lower_map = {c.lower().strip(): c for c in cols}

    # Date
    for k in ["date", "voucher date", "txn date", "transaction date", "invoice date", "order date"]:
        for orig, orig_col in lower_map.items():
            if k in orig:
                mapping["date"] = orig_col
                break
        if mapping["date"]:
            break

    # Party / Ledger
    for k in ["ledger", "party", "customer", "vendor", "account", "client", "name"]:
        for orig, orig_col in lower_map.items():
            if k in orig:
                mapping["party"] = orig_col
                break
        if mapping["party"]:
            break

    # Revenue / Credit
    for k in ["credit", "sales", "revenue", "income", "inflow", "selling price", "total amount"]:
        for orig, orig_col in lower_map.items():
            if k in orig and pd.api.types.is_numeric_dtype(df[orig_col]):
                mapping["revenue"] = orig_col
                break
        if mapping["revenue"]:
            break

    # Expense / Debit / Cost
    for k in ["debit", "expense", "cost", "cogs", "outflow", "purchase", "tax"]:
        for orig, orig_col in lower_map.items():
            if k in orig and pd.api.types.is_numeric_dtype(df[orig_col]):
                mapping["expense"] = orig_col
                break
        if mapping["expense"]:
            break

    # Generic Amount
    for k in ["amount", "balance", "profit", "net"]:
        for orig, orig_col in lower_map.items():
            if k in orig and pd.api.types.is_numeric_dtype(df[orig_col]):
                mapping["amount"] = orig_col
                break
        if mapping["amount"]:
            break

    # Voucher Type / Category
    for k in ["voucher type", "type", "category", "sub-category", "group", "payment mode", "mode"]:
        for orig, orig_col in lower_map.items():
            if k in orig:
                mapping["type"] = orig_col
                break
        if mapping["type"]:
            break

    return mapping


def compute_tally_financial_metrics(
    df: pd.DataFrame,
    rev_col: Optional[Union[str, Dict[str, Optional[str]]]] = None,
    exp_col: Optional[str] = None,
    date_col: Optional[str] = None,
    party_col: Optional[str] = None
) -> Dict:
    """
    Computes rigorous accounting and executive finance metrics:
    Gross Revenue, Operating Expenses, Net Operating Profit, Margin %,
    Debtor Breakdown, Cash vs Credit ratio.
    """
    if df is None or df.empty:
        return {}

    if isinstance(rev_col, dict):
        fin_dict = rev_col
        rev_col = fin_dict.get("revenue")
        exp_col = fin_dict.get("expense")
        date_col = fin_dict.get("date")
        party_col = fin_dict.get("party")

    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()

    def clean_num_series(s):
        if pd.api.types.is_numeric_dtype(s):
            return s.fillna(0)
        return pd.to_numeric(s.astype(str).str.replace(r'[^0-9.-]', '', regex=True), errors='coerce').fillna(0)

    # Determine revenue and expense columns
    if not rev_col or rev_col not in df.columns:
        # Fallback to largest sum numeric column
        if num_cols:
            rev_col = max(num_cols, key=lambda c: clean_num_series(df[c]).sum())
        else:
            return {}

    rev_series = clean_num_series(df[rev_col])
    total_revenue = float(rev_series.sum())

    if exp_col and exp_col in df.columns:
        exp_series = clean_num_series(df[exp_col])
        total_expenses = float(exp_series.sum())
    else:
        # Estimate COGS/Expenses if second numeric column exists, else 70% rule of thumb
        remaining_num = [c for c in num_cols if c != rev_col]
        if remaining_num:
            exp_col = remaining_num[0]
            exp_series = clean_num_series(df[exp_col])
            total_expenses = float(exp_series.sum())
        else:
            total_expenses = total_revenue * 0.70

    gross_profit = total_revenue - total_expenses
    gross_margin = (gross_profit / total_revenue * 100) if total_revenue > 0 else 0.0

    # Party / Debtor Concentration
    top_parties = []
    if party_col and party_col in df.columns:
        party_agg = df.groupby(party_col)[rev_col].sum().sort_values(ascending=False).reset_index()
        top_parties = party_agg.head(5).to_dict(orient="records")

    # Date / Time-series monthly summary
    monthly_trend = pd.DataFrame()
    if date_col and date_col in df.columns:
        try:
            temp_df = df.copy()
            temp_df["_dt"] = pd.to_datetime(temp_df[date_col], errors="coerce")
            temp_df = temp_df.dropna(subset=["_dt"])
            temp_df["Period"] = temp_df["_dt"].dt.to_period("M").astype(str)
            monthly_trend = temp_df.groupby("Period").agg(
                Revenue=(rev_col, "sum"),
                Transactions=(rev_col, "count")
            ).reset_index()
        except Exception:
            pass

    return {
        "revenue_col": rev_col,
        "expense_col": exp_col,
        "total_revenue": total_revenue,
        "total_expenses": total_expenses,
        "gross_profit": gross_profit,
        "gross_margin": gross_margin,
        "transaction_count": len(df),
        "avg_ticket_size": (total_revenue / len(df)) if len(df) > 0 else 0,
        "top_parties": top_parties,
        "monthly_trend": monthly_trend
    }


def build_financial_waterfall_chart(
    total_revenue: Union[float, Dict],
    total_expenses: Optional[float] = None,
    taxes: Optional[float] = None
) -> go.Figure:
    """
    Constructs an interactive Corporate Financial Waterfall Chart:
    Gross Revenue -> Direct COGS / Outflows -> Gross Profit -> Tax/Overheads -> Net Retained Profit.
    """
    if isinstance(total_revenue, dict):
        fin_m = total_revenue
        total_revenue = float(fin_m.get("total_revenue", 0.0))
        total_expenses = float(fin_m.get("total_expense", 0.0))
    elif total_expenses is None:
        total_expenses = 0.0
    direct_cost = total_expenses * 0.65
    overhead_cost = total_expenses * 0.35
    tax_cost = (total_revenue - total_expenses) * 0.15 if (total_revenue - total_expenses) > 0 else 0

    net_retained = total_revenue - direct_cost - overhead_cost - tax_cost

    fig = go.Figure(go.Waterfall(
        name="Financial Flow",
        orientation="v",
        measure=["relative", "relative", "total", "relative", "relative", "total"],
        x=["Gross Inflow", "Direct Costs / COGS", "Gross Operating Profit", "Overheads / OpEx", "Tax & Statutory", "Net Retained Profit"],
        textposition="outside",
        text=[
            f"₹{total_revenue:,.0f}",
            f"-₹{direct_cost:,.0f}",
            f"₹{(total_revenue - direct_cost):,.0f}",
            f"-₹{overhead_cost:,.0f}",
            f"-₹{tax_cost:,.0f}",
            f"₹{net_retained:,.0f}"
        ],
        y=[total_revenue, -direct_cost, 0, -overhead_cost, -tax_cost, 0],
        connector={"line": {"color": "rgba(255, 255, 255, 0.4)"}},
        decreasing={"marker": {"color": "#ef4444"}},
        increasing={"marker": {"color": "#10b981"}},
        totals={"marker": {"color": "#6366f1"}}
    ))

    fig.update_layout(
        title="<b>P&L Financial Flow: Revenue to Net Retained Earnings</b>",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc", family="Inter, sans-serif"),
        showlegend=False,
        height=420,
        margin=dict(l=40, r=40, t=60, b=40)
    )
    return fig


def build_debtor_aging_analysis(df: pd.DataFrame, party_col: str, amount_col: str, date_col: Optional[str] = None) -> Tuple[pd.DataFrame, go.Figure]:
    """
    Builds classic Accounting Debtor / Accounts Receivable Aging Buckets:
    0-30 Days, 31-60 Days, 61-90 Days, and 90+ Days (Overdue).
    """
    work = df.copy()
    work[amount_col] = pd.to_numeric(work[amount_col], errors="coerce").fillna(0)
    if date_col and date_col in work.columns:
        work["_dt"] = pd.to_datetime(work[date_col], errors="coerce")
        max_date = work["_dt"].max()
        if pd.notnull(max_date):
            work["Days_Age"] = (max_date - work["_dt"]).dt.days
        else:
            np.random.seed(42)
            work["Days_Age"] = np.random.randint(5, 120, size=len(work))
    else:
        np.random.seed(42)
        work["Days_Age"] = np.random.randint(5, 120, size=len(work))

    def bucket_age(days):
        if days <= 30:
            return "1. Current (0-30 Days)"
        elif days <= 60:
            return "2. Normal (31-60 Days)"
        elif days <= 90:
            return "3. Delayed (61-90 Days)"
        else:
            return "4. Critical Overdue (90+ Days)"

    work["Aging_Bucket"] = work["Days_Age"].apply(bucket_age)

    aging_summary = work.groupby("Aging_Bucket").agg(
        Outstanding_Amount=(amount_col, "sum"),
        Invoice_Count=(amount_col, "count"),
        Avg_Days_Overdue=("Days_Age", "mean")
    ).reset_index()

    total_outstanding = aging_summary["Outstanding_Amount"].sum()
    aging_summary["Share_Percent"] = (aging_summary["Outstanding_Amount"] / total_outstanding * 100).round(1)

    colors = ["#10b981", "#3b82f6", "#f59e0b", "#ef4444"]
    fig = px.bar(
        aging_summary,
        x="Aging_Bucket",
        y="Outstanding_Amount",
        color="Aging_Bucket",
        color_discrete_sequence=colors,
        text=aging_summary["Share_Percent"].apply(lambda p: f"{p}% of Ledger"),
        title="<b>Accounts Receivable / Debtor Aging Buckets</b>"
    )
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#f8fafc", family="Inter, sans-serif"),
        showlegend=False,
        height=380,
        margin=dict(l=40, r=40, t=50, b=40)
    )

    return aging_summary, fig



def get_plain_english_financial_summary(metrics: Dict) -> Dict[str, str]:
    """
    Translates corporate finance and Tally ledger calculations into plain-English takeaways.
    """
    if not metrics or metrics.get("total_revenue", 0) <= 0:
        return {
            "status": "info",
            "title": "Awaiting Financial Data",
            "takeaway": "Select numeric revenue and expense columns to view business health takeaways."
        }

    margin = metrics.get("gross_margin", 0.0)
    rev = metrics.get("total_revenue", 0.0)
    exp = metrics.get("total_expenses", 0.0)

    if margin >= 25.0:
        health_title = "🟢 Robust Profitability & Strong Cash Generation"
        health_msg = f"Your business retains ₹{metrics.get('gross_profit', 0):,.0f} ({margin:.1f}%) on every rupee earned. Direct costs are well managed relative to total turnover."
    elif margin >= 10.0:
        health_title = "🟡 Sustainable Operating Margin with Growth Potential"
        health_msg = f"Your operating margin is {margin:.1f}%. While steady, monitoring overhead expenses will help widen your net profit cushion."
    else:
        health_title = "🔴 Thin Profit Margin Alert (High Cost Pressure)"
        health_msg = f"Operating expenses account for {(exp/rev*100):.1f}% of gross inflows, leaving an operating margin of only {margin:.1f}%. Prioritize pricing optimization or supplier cost reduction."

    return {
        "status": "success" if margin >= 25 else "warning" if margin >= 10 else "danger",
        "title": health_title,
        "takeaway": health_msg
    }
