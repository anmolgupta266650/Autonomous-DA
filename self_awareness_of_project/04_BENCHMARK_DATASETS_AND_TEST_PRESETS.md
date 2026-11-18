# 📘 Chapter 4: Benchmark Datasets & Module Test Presets

To ensure evaluators and senior leaders can verify every analytical capability instantly without needing to prepare external files, Autonomous DA comes pre-seeded with **6 authentic real-world benchmark datasets** and **8 dedicated module test presets**.

---

## 4.1 The 6 Pre-Seeded Real Benchmark Datasets

Each dataset is stored locally in `data/` and pre-configured with realistic distributions:

| Dataset Display Name | File Path | Records | Features | Real-World Origin & Use Case |
| :--- | :--- | :--- | :--- | :--- |
| **💼 SME Accounting & Ledger (Tally-Style)** | `data/sme_tally_financial_ledger.csv` | 1,000 | 9 | Real-world Indian corporate accounting ledger (GST rates, Sundry Debtors, Debit/Credit turnover, and invoice numbers). |
| **🎓 College Students & Admissions** | `data/college_university_admissions.csv` | 1,200 | 8 | Standardized university admissions dataset (High School GPA, SAT scores, University Tiers, Admission decisions). |
| **🛒 Global Superstore Sales** | `data/global_superstore_2024.csv` | 1,200 | 12 | Commercial retail sales dataset across 4 global regions, 3 customer categories, shipping modes, and net profitability. |
| **📡 IBM Telco Customer Churn** | `data/telco_customer_churn_real.csv` | 1,200 | 11 | Telecom subscription retention dataset (Monthly charges, tenure, contract types, and binary customer churn labels). |
| **🏡 California Housing Economics** | `data/california_housing_real.csv` | 1,500 | 9 | Authentic US Census Bureau housing economics dataset (Median income, house age, average rooms, median property valuation). |
| **🔬 Healthcare Clinical Diagnostics** | `data/healthcare_clinical_diagnostics.csv` | 569 | 11 | Real clinical oncology diagnostic biopsy dataset (Cell radius, texture, perimeter, smoothness, and benign/malignant diagnosis). |

---

## 4.2 The 8 Dedicated Module Test Presets

In the sidebar or Home page evaluation hub, choosing a preset primes the dataset and navigates directly to the target studio:

### Preset 1: 💼 Tally Corporate Finance Test Preset
* **Target Studio**: `Finance & Science Studios` (Page 4)
* **Dataset Used**: `SME Accounting & Ledger` (1,000 records)
* **Key Attributes**: `Party_Name`, `Voucher_Type`, `Debit`, `Credit`, `Payment_Status`
* **What Authorities Test**: P&L Turnover Waterfall, Debtor Aging buckets (0-30, 31-60, 61-90, 90+ days), and What-If sensitivity sliders.

### Preset 2: 🕵️ Accounting & Forensic Fraud (Benford's Law) Test Preset
* **Target Studio**: `Finance & Science Studios` (Page 4)
* **Dataset Used**: `SME Accounting & Ledger` (1,000 records)
* **Key Attributes**: `Credit_Amount`, `Party_Name`, `Voucher_No`
* **What Authorities Test**: Benford's Law Chi-Square distribution plot, duplicate invoice disbursement detector, and round-number transaction spikes.

### Preset 3: 🔬 Academic Research & APA 7th Paper Test Preset
* **Target Studio**: `Finance & Science Studios` (Page 4)
* **Dataset Used**: `College Students & Admissions` (1,200 records)
* **Key Attributes**: `Admission_Status`, `High_School_GPA`, `SAT_Score`
* **What Authorities Test**: Auto-formulation of null ($H_0$) and alternate ($H_1$) hypotheses, Welch's Two-Sample t-test, One-Way ANOVA, OLS regression, and 1-click generation of a 7-section APA 7th Edition academic paper.

### Preset 4: 🖥️ Power BI & Dynamic Pivot Studio Test Preset
* **Target Studio**: `Data & BI Studio` (Page 2)
* **Dataset Used**: `Global Superstore Sales` (1,200 records)
* **Key Attributes**: `Region`, `Product_Category`, `Sales_Amount`, `Net_Profit`
* **What Authorities Test**: Multi-dimensional pivot matrix with grand totals, and real-time DAX calculations (% Contribution to Total, Cumulative YTD, Moving Average).

### Preset 5: 🤖 Predictive AI Churn Classification Test Preset
* **Target Studio**: `AI Intelligence & Copilot` (Page 3)
* **Dataset Used**: `IBM Telco Customer Churn` (1,200 records)
* **Key Attributes**: `Churn` (Target), `MonthlyCharges`, `Tenure_Months`, `Contract`
* **What Authorities Test**: Auto task inference (`classification`), 5-fold cross-validated model leaderboard (Logistic Regression, Random Forest, Gradient Boosting), and feature importance ranking.

### Preset 6: 🏡 Predictive AI Housing Valuation Regression Test Preset
* **Target Studio**: `AI Intelligence & Copilot` (Page 3)
* **Dataset Used**: `California Housing Economics` (1,500 records)
* **Key Attributes**: `Median_House_Value` (Target), `Median_Income`, `Avg_Rooms`
* **What Authorities Test**: Continuous regression benchmarking (Linear Regression, Ridge, Random Forest), $R^2$ variance explained, MAE, and RMSE scores.

### Preset 7: 🧹 Data Cleaning Sentinel Test Preset
* **Target Studio**: `Data & BI Studio` (Page 2)
* **Dataset Used**: `Synthetic Dirty Benchmark` (515 records)
* **Key Attributes**: `Annual_Salary`, `Transaction_Value`, `Department`
* **What Authorities Test**: Automated discovery and repair of intentionally injected NaNs, duplicate records, and extreme salary outliers ($> \$450,000$).

### Preset 8: 💬 Conversational AI Copilot 2.0 Test Preset
* **Target Studio**: `AI Intelligence & Copilot` (Page 3)
* **Dataset Used**: `Global Superstore Sales` (1,200 records)
* **What Authorities Test**: Plain-English queries, sandboxed Python code execution, and instant chart synthesis.

---

## 4.3 The Synthetic Corruption Engine (`generate_dirty_test_dataset`)

To mathematically prove that Autonomous DA cleans real-world messy data without crashing, `modules/module_test_registry.py` includes a deterministic corruption injector:

```python
# Exact corruption rules injected for audit testing:
1. 35 Missing Cells (NaNs) injected into continuous and categorical columns.
2. 15 Exact Duplicate Rows cloned from earlier indices.
3. 8 Extreme Outlier Spikes (Salary numbers between $450,000 and $990,000, 10x normal distribution).
4. Dirty String Whitespace & Inconsistent Boolean Values ('True', 'False', 'Yes', 'No').
```

When an evaluator runs the **Data Cleaning Sentinel**, they can watch the cleaning engine identify and repair every single one of these 4 anomalies, raising the health score from **~62/100 to a perfect 100/100**!

---
*Autonomous DA Enterprise &bull; Chapter 4 &bull; Datasets & Test Presets*
