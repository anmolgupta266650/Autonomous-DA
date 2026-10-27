import pandas as pd
import numpy as np


def generate_executive_insights(df: pd.DataFrame):
    """
    Analyzes dataset patterns and generates human-readable business insights,
    Pareto concentration alerts, statistical anomalies, and tactical recommendations.
    """
    if df is None or df.empty:
        return []

    insights = []
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category", "string"]).columns.tolist()

    # 1. Dataset Scale & Cleanliness Health Insight
    total_records = len(df)
    missing_sum = df.isnull().sum().sum()
    if missing_sum == 0:
        insights.append({
            "type": "success",
            "category": "Data Quality",
            "title": "High Data Fidelity",
            "description": f"The dataset contains {total_records:,} complete records with 0 missing cells, making it production-ready for reporting and machine learning."
        })
    else:
        insights.append({
            "type": "warning",
            "category": "Data Hygiene",
            "title": f"Missingness Detected ({missing_sum} cells)",
            "description": "Some fields contain null values. Recommend running the automated Imputation module before deploying predictive models."
        })

    # 2. Pareto 80/20 Concentration Analysis
    if len(cat_cols) > 0 and len(num_cols) > 0:
        cat = cat_cols[0]
        # Choose a suitable numeric metric (e.g. sales, profit, cost, or first num col)
        metric = num_cols[0]
        for col in num_cols:
            if any(k in col.lower() for k in ["sales", "profit", "revenue", "cost", "amount", "charge", "tuition", "fee", "scholarship", "chance"]):
                metric = col
                break

        grouped = df.groupby(cat)[metric].sum().sort_values(ascending=False)
        total_val = grouped.sum()
        if total_val > 0:
            top_entity = grouped.index[0]
            top_share = (grouped.iloc[0] / total_val) * 100
            
            # Check if top 20% categories account for ~80%
            top_20_count = max(1, int(len(grouped) * 0.2))
            top_20_share = (grouped.iloc[:top_20_count].sum() / total_val) * 100

            insights.append({
                "type": "info",
                "category": "Pareto Concentration",
                "title": f"Dominant Segment: {top_entity}",
                "description": f"'{top_entity}' drives {top_share:.1f}% of total {metric}. Furthermore, the top {top_20_count} category segment(s) represent {top_20_share:.1f}% of aggregate {metric}."
            })

    # 3. High Correlation & Key Drivers
    if len(num_cols) >= 2:
        corr_matrix = df[num_cols].corr(numeric_only=True)
        pairs = []
        cols = corr_matrix.columns.tolist()
        for i in range(len(cols)):
            for j in range(i + 1, len(cols)):
                c1, c2 = cols[i], cols[j]
                val = corr_matrix.loc[c1, c2]
                if not np.isnan(val):
                    pairs.append((c1, c2, val, abs(val)))
        if pairs:
            pairs.sort(key=lambda x: x[3], reverse=True)
            top_pair = pairs[0]
            if top_pair[3] >= 0.45:
                col1, col2, actual_corr = top_pair[0], top_pair[1], top_pair[2]
                relationship = "positive" if actual_corr > 0 else "inverse"
                insights.append({
                    "type": "info",
                    "category": "Driver Analysis",
                    "title": f"Strong Co-dependency: {col1} & {col2}",
                    "description": f"A notable {relationship} correlation (r = {actual_corr:.2f}) exists between '{col1}' and '{col2}'. Changes in one will directly impact the other."
                })

    # 4. Outlier & Operational Risk Flag
    for col in num_cols[:3]:
        s = df[col].dropna()
        if len(s) > 10:
            q1, q3 = s.quantile(0.25), s.quantile(0.75)
            iqr = q3 - q1
            outliers = ((s < (q1 - 1.5 * iqr)) | (s > (q3 + 1.5 * iqr))).sum()
            if outliers > 0 and (outliers / len(s)) > 0.03:
                insights.append({
                    "type": "warning",
                    "category": "Variance & Risk",
                    "title": f"Outlier Sensitivity in '{col}'",
                    "description": f"{outliers} extreme values ({outliers/len(s)*100:.1f}% of rows) identified in '{col}'. May skew arithmetic averages; consider median or IQR clamping."
                })
                break

    # 5. Strategic Recommendation
    if len(cat_cols) > 0 and len(num_cols) > 0:
        insights.append({
            "type": "recommendation",
            "category": "Strategic Action",
            "title": "Optimization Opportunity",
            "description": f"Focus resource allocation on the upper quartile segments of '{cat_cols[0]}' to maximize ROI, while establishing threshold alerts for high variance metrics."
        })

    return insights
