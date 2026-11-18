# 📘 Chapter 2: The 5 Flagship Studios & UI Pages Deep-Dive

Autonomous DA consolidates all data workflows into **5 Flagship Studios** in the `pages/` directory, managed by the central router in `app.py`. This chapter explains every studio page, every tab, and the exact workflows they provide.

---

## 🏛️ Studio 1: Executive Launchpad (`pages/1_Home.py`)

The **Home Page** serves as the central landing page, quick launcher, and authority evaluation control room.

### Tab 1: 🚀 Platform Overview & 1-Click Auto-Pilot
* **1-Click Autonomous Auto-Pilot**:
  * An analyst who has never seen the dataset before can simply click **"⚡ Run 1-Click Auto-Pilot Audit"**.
  * The engine profiles the data, determines whether it is *Financial*, *Sales*, *Clinical*, or *Academic*, cleans corrupted cells in memory, computes key metrics, and displays an executive summary card with a plain-English takeaway.
* **4 Flagship Studio Cards**:
  * Provides quick-access navigation cards to jump directly into the Data Studio, AI Hub, Finance & Science Studios, or Executive Export.

### Tab 2: 🧪 Authority Evaluation & Function Verification
* **8/8 Automated Engine Self-Test**:
  * Built specifically for professors, senior leaders, and technical evaluators.
  * Clicking **"Run Full System Diagnostic"** runs real-time micro-benchmarks across all 8 core subsystems (Cleaner, Feature Builder, DAX Engine, AI Sandbox, Tally Finance, Research Studio, PPTX Generator, and Database Checkpoints).
  * Evaluators see an instant verification table with execution latencies (<10ms) and **100% GREEN PASS** confirmation.
* **1-Click Module-Specific Test Presets**:
  * Contains 8 pre-configured test cards (e.g. *Tally Finance*, *Academic Research*, *Power BI Pivot*, *AutoML Churn*, *Data Cleaning Sentinel*).
  * Clicking **"Prime & Launch"** instantly loads the dedicated dataset, seeds known parameters, and switches directly to the relevant studio page for immediate testing.

---

## 📊 Studio 2: Data & BI Studio (`pages/2_Data_Studio.py`)

The **Data & BI Studio** is the all-in-one workspace for data exploration, spreadsheet editing, data cleaning, executive dashboards, and Power BI DAX pivots.

### Tab 1: 📋 Smart Spreadsheet Grid
* **In-Browser Interactive Grid**:
  * Built using Streamlit Data Editor with full keyboard navigation (arrow keys, double-click to edit cells).
  * Allows analysts to edit values directly, add new rows, or delete records without opening Microsoft Excel.
  * Includes a search bar and quick column sorters.

### Tab 2: 🧹 Data Cleaner & Feature Lab
* **Automated Data Quality Assessment**:
  * Displays a real-time **Data Health Score (0-100)** based on missing rate, duplicate frequency, and outlier severity.
* **7-Operation Cleaning Sentinel**:
  1. *Missing Cell Imputation*: Replace NaNs with Mean, Median, Mode, or custom constant.
  2. *Duplicate Elimination*: Removes identical records with 1 click while tracking removed count.
  3. *Type Casting*: Cast columns to Integer, Float, String, Datetime, or Category safely.
  4. *Outlier Detection & Clamping*: Uses IQR (Tukey's Fences) or Z-score boundaries with Winsorization (clamping extreme spikes to boundary limits rather than deleting valid records).
  5. *Column Dropping & Renaming*: Strip unneeded identifiers or rename headers.
  6. *Conditional Row Filtering*: Filter records dynamically using operators (`>`, `<`, `==`, `!=`, `contains`).
* **Feature Engineering Lab**:
  * *Math Operations*: Add, subtract, multiply, or divide two columns (e.g., `Price * Quantity = Total_Sales`).
  * *Mathematical Transforms*: Logarithmic (`log1p`), Square Root, or Standard Z-Score normalization.
  * *Date Feature Extraction*: Automatically extract Year, Month, Quarter, Day of Week, or Is_Weekend.
  * *Binning & Discretization*: Split continuous numbers into Low, Medium, High quantile or uniform tiers.
  * *Conditional Flags*: Create binary indicator flags (e.g., `If Rating >= 4 -> 'High_Performer'`).

### Tab 3: 📈 Executive BI Dashboard & Custom Visualizer
* **Automated 4-Grid Cross-Visuals**:
  * Automatically scans for the highest-cardinality dimension and strongest metric to render an executive 4-chart layout (Bar breakdown, Category distribution, Correlation view, and Trend over time).
* **Custom Plotly Visual Builder**:
  * Choose from 10 chart types: *Bar Chart*, *Line Chart*, *Area Chart*, *Scatter Plot*, *Histogram / Distribution*, *Box Plot*, *Violin Plot*, *Treemap*, *Pie / Donut*, and *Sunburst*.
  * Built-in Dark Cyber Themes: *Cyber Indigo*, *Emerald Mint*, *Amber Gold*, and *Rose Crimson*.

### Tab 4: 🖥️ Pivot & Power BI DAX Matrix Studio
* **Multi-Dimensional Pivot Matrix**:
  * Group rows by multiple dimensions (e.g., `Region` ➔ `Category`) and aggregate values (`Sum`, `Average`, `Count`, `Min`, `Max`).
  * Displays grand total margins and flattens column hierarchies for clean reading.
* **Power BI DAX Calculation Engine**:
  * Computes industry-standard DAX measures on the fly:
    1. `% Contribution to Total`: `DIVIDE([Metric], CALCULATE(SUM([Metric]), ALL()))`
    2. `Cumulative Running Total`: Running YTD progression over time.
    3. `3-Period Moving Average`: Smoothed trend line removing short-term noise.
    4. `Period-over-Period Growth Rate`: Percentage expansion or contraction.

---

## 🤖 Studio 3: AI Intelligence & Copilot Hub (`pages/3_AI_Hub.py`)

The **AI Intelligence Hub** bridges conversational artificial intelligence with rigorous data science.

### Tab 1: 💬 Conversational AI Copilot
* **Dual-Mode Intelligence**:
  1. *Local Heuristic Mode (100% Offline)*: Detects 10 analytical intents locally (Outlier scans, top-N rankings, category comparisons, revenue trends, null distributions). Operates completely offline with zero API keys.
  2. *Frontier Cloud LLM Mode (BYOK)*: Expander allows users to plug in their own Google Gemini or OpenAI API key for deep natural language reasoning.
* **Interactive Code & Chart Generation**:
  * Every Copilot response returns the plain-English answer, an interactive Plotly chart, and the exact Python Pandas code executed.

### Tab 2: 🐍 Sandboxed Python Code Interpreter
* **Isolated AST Runtime**:
  * Users can write and execute arbitrary Python Pandas code directly inside the web browser.
  * Safely captures console `stdout`, output DataFrames, and Plotly `fig` objects.
  * Security protection: Prohibits `eval`, `exec`, `open`, `__import__`, `os`, and `sys` to prevent host machine attacks.

### Tab 3: 🚀 1-Click Auto-Pilot
* Runs an automated end-to-end data audit, determines the domain, and synthesizes top findings into an executive briefing card.

### Tab 4: 🤖 Predictive Machine Learning (AutoML)
* **Automated Task Type Detection**: Automatically checks target cardinality to decide whether to run **Classification** (Logistic Regression, Random Forest, Gradient Boosting) or **Regression** (Linear Regression, Ridge, Decision Tree, Random Forest).
* **5-Fold Cross-Validation Leaderboard**: Evaluates models across standard metrics (Accuracy, ROC-AUC, F1, Precision, Recall for classification; $R^2$, MAE, RMSE for regression).
* **Feature Importance Ranking**: Renders a horizontal bar chart showing which attributes most heavily influence the prediction.

---

## 💼 Studio 4: Finance & Science Studios (`pages/4_Finance_Science.py`)

This studio unifies corporate accounting with empirical academic research.

### Tab 1: 💼 Tally Corporate P&L & Turnover Statements
* **Accounting Group Mapping**: Ingests Tally ERP / Prime XML and Excel ledgers, mapping accounts into *Sales Accounts*, *Direct Expenses*, *Sundry Debtors*, and *Bank Accounts*.
* **P&L Turnover Waterfall**: Visualizes Gross Revenue, Cost of Goods Sold (COGS), Gross Profit, and Operating Margin in an executive financial waterfall chart.
* **Debtor Aging Buckets**: Categorizes outstanding accounts receivable into `0-30 Days (Current)`, `31-60 Days (Normal)`, `61-90 Days (Delayed)`, and `90+ Days (Critical Overdue)`.

### Tab 2: 🕵️ Forensic Auditor & Anomaly Sentinel
* **Benford's Law Chi-Square Audit**:
  * Evaluates the first-digit distribution of transaction amounts against Benford's theoretical probability:
    $$P(d) = \log_{10}\left(1 + \frac{1}{d}\right)$$
  * Runs a **Chi-Square Goodness-of-Fit test** ($\chi^2$). A $p$-value $< 0.05$ flags intentional invoice fabrication, employee kickbacks, or threshold evasion.
* **Duplicate Disbursement Sentinel**: Flags identical invoice sums disbursed to the same vendor on the same date.
* **Round-Number Anomaly Clusters**: Detects excessive clusters of exact round amounts (e.g. ₹50,000, ₹100,000) often used to bypass secondary management approval tiers.

### Tab 3: 🎯 Dynamic What-If Sensitivity Simulator
* Interactive parameter sliders allow CFOs to stress-test their business:
  * Adjust Revenue Growth ($\pm 30\%$).
  * Adjust COGS Escalation ($\pm 25\%$).
  * Adjust Overhead Fluctuations ($\pm 20\%$).
* Displays real-time delta scorecards showing forecasted Net Margin and Breakeven Runway.

### Tab 4: 🔬 Academic Research & APA 7th Edition Paper Generator
* **Automated Hypothesis Formulation**: Discovers categorical independent variables and continuous dependent metrics, formulating null ($H_0$) and alternate ($H_1$) hypotheses automatically.
* **Statistical Hypothesis Engines**:
  1. *Welch's Two-Sample t-test*: Handles unequal group variances, computing $t$-statistic, $p$-value, and Cohen's $d$ effect size.
  2. *One-Way ANOVA*: Computes $F$-statistic and omnibus $p$-value across multiple factor levels.
  3. *Multivariate OLS Econometric Regression*: Models $Y = \beta_0 + \beta_1 X_1 + \dots + \epsilon$, returning $R^2$, adjusted $R^2$, $F$-stat, coefficient standard errors, and $t$-probabilities.
* **1-Click APA 7th Edition Paper Synthesis**:
  * Assembles a complete academic empirical research paper including: **Title Page, Structured Abstract, Introduction & Hypotheses, Methodology, Results with Formatted Tables, Discussion, and APA References**.
  * Downloadable as Markdown or HTML.

---

## 📥 Studio 5: Executive Reports & Decks (`pages/5_Executive_Export.py`)

The final studio packages insights into tangible, boardroom-ready deliverables.

### Tab 1: 📑 PowerPoint (.pptx) & 16:9 Decks
* **10-Slide Microsoft PowerPoint Presentation**:
  * Generates an editable `.pptx` file formatted in modern 16:9 widescreen layout with corporate dark theme typography, KPI metric callouts, segment rankings, risk assessments, and strategic roadmaps.
  * 100% compatible with Microsoft PowerPoint, Google Slides, and Apple Keynote.
* **Interactive Web Deck**: Renders a browser-based slide deck with live presentation controls.

### Tab 2: 🌐 Executive HTML Intelligence Report
* A single, self-contained HTML file containing KPI scorecards, automated insights, and benchmark charts.
* Designed with print CSS: press `Ctrl + P ➔ Save as PDF` for a flawless executive briefing document.

### Tab 3: 📑 Formatted Excel (.xlsx) & CSV
* Exports a multi-column styled workbook with colored header rows, auto-fitted column widths, and preserved numerical precision.

### Tab 4: 💾 Data Lineage & Audit Checkpoints
* Displays all historical pipeline snapshots stored in SQLite (`data/projects.db`).
* Allows 1-click **Rollback to Previous Checkpoint** if an analyst needs to undo a transformation.

### Tab 5: 🛡️ Enterprise Governance & Compliance Certificate
* **Cryptographic SHA-256 Digest**: Computes a unique cryptographic fingerprint of the active dataset state.
* **SOX Section 404 & GDPR Article 30 Attestation**: Certified statement confirming zero remote data exfiltration, local in-memory execution, and immutable audit provenance.
* **Corporate Alert Webhook Simulator**: Demonstrates real-time integration with corporate Slack and Microsoft Teams channels, displaying adaptive card JSON payloads for forensic alerts.

---
*Autonomous DA Enterprise &bull; Chapter 2 &bull; The 5 Flagship Studios*
