# 📘 Autonomous DA — Complete Beginner's User Manual
### *Step-by-Step Guide for Absolute Beginners to Run, Explore, and Master the Platform*

Welcome to **Autonomous DA**! This manual was written specifically for you. Even if you have never run a Python script or worked with data analytics software before, this guide will walk you through every single step with zero confusion.

---

## ⚡ Method 1: The 1-Click Launch (The Easiest & Fastest Way)

If you are on Windows, you don't even need to open a terminal:

1. Open your project folder: `projectDA`.
2. Find the file named **`Launch_Autonomous_DA.bat`**.
3. **Double-click it!**
4. A small terminal window will open, start the platform, and automatically launch your default web browser to:
   👉 **`http://localhost:8501`**

*(That's it! You are now running the platform locally!)*

---

## 💻 Method 2: Running via Terminal (PowerShell or Command Prompt)

If you prefer to start it from the terminal or are presenting from a command line:

### Step 1: Open PowerShell or Command Prompt
* Press the `Windows Key`, type **PowerShell**, and press `Enter`.
* Navigate to your project directory:
  ```powershell
  cd "C:\Users\M S I\OneDrive - Office\Desktop\projectDA"
  ```

### Step 2: Activate the Virtual Environment
```powershell
.\.venv\Scripts\activate
```
*(You will see `(.venv)` appear at the start of your prompt, meaning your isolated Python environment is active).*

### Step 3: Start the Application
```powershell
streamlit run app.py
```
After 2-3 seconds, your browser will open automatically to **`http://localhost:8501`**.

---

## 🔐 Logging In: Enterprise Accounts Cheat Sheet

When the application loads, you will see the **Enterprise Single Sign-On** screen. You can either type credentials manually or click any of the **Quick 1-Click Role Switcher buttons**:

| Enterprise Role | Username | Password | Best For | What You Can Access |
| :--- | :--- | :--- | :--- | :--- |
| **👑 Administrator** | `admin` | `admin123` | Demonstrations & Evaluations | **Full Platform** (All 4 Flagship Studios, Engine Diagnostics & Exports) |
| **💼 CFO / Accountant** | `cfo_accountant` | `tally123` | Financial Audits | Data Studio, Tally P&L, Forensic Benford Fraud Auditor, Executive Reports |
| **🔬 Research Scientist**| `researcher` | `science123` | Academic Studies | Data Studio, AI Intelligence Hub, APA 7th Edition Paper Generator |
| **📊 Executive Viewer** | `executive` | `exec123` | Senior Leadership | Read-Only Interactive Dashboards, 10-Slide PowerPoint Exports |

> **Beginner Tip:** For full access during your demonstration, click **👑 Administrator** or log in with `admin` / `admin123`.

---

## 🧭 Your First 5 Minutes: The Complete Beginner Walkthrough

Here is the exact journey from raw data to a finished boardroom presentation:

```
[1. Home: Health Test] ➔ [2. Data Studio: Auto-Clean] ➔ [3. AI Hub: Copilot] ➔ [4. Finance: Fraud Audit] ➔ [5. Export: Download PPTX]
```

### 1️⃣ Step 1: Verify System Health (Home Page)
1. On the **Home** page, look at the sidebar or the main page.
2. Click **Tab 2: Authority Evaluation & Function Verification**.
3. Click the purple button: **"🧪 Run Full System Diagnostic"**.
4. Watch all **8/8 core subsystems light up GREEN**. This proves to anyone watching that the database, cleaning algorithms, DAX engines, and sandboxes are 100% operational.

---

### 2️⃣ Step 2: Explore & Auto-Clean Dirty Data (Data & BI Studio)
1. In the sidebar under **"Active Data Source"**, select **"🧪 Module Test Presets"**.
2. Pick **"🧹 Data Cleaning & Preprocessing Sentinel Test Preset"** and click **"⚡ Prime Dataset for This Module"**.
3. In the left navigation menu, click **📊 Data & BI Studio**.
4. Go to **Tab 2: Data Cleaner & Feature Lab**:
   * You will see missing cells (NaNs) and duplicate rows flagged automatically.
   * Under *Missing Value Imputation*, select strategy **"Median"** and click **"Apply Imputation"**.
   * Under *Duplicate Elimination*, click **"Remove All Duplicate Rows"**.
   * Under *Outlier Detection*, select **"IQR (Tukey's Fences)"** with action **"Clamp to Boundaries (Winsorize)"** and click **"Handle Outliers"**.
5. Your dataset is now clean with a **100/100 Data Health Score**!

---

### 3️⃣ Step 3: Ask the AI Copilot & Run AutoML (AI Intelligence Hub)
1. In the left navigation menu, click **🤖 AI Intelligence & Copilot**.
2. Go to **Tab 1: Conversational AI Copilot**:
   * Click any suggested prompt (e.g., *"Show top performing categories"* or *"Check for statistical outliers"*).
   * Notice that the AI answers immediately, generates an interactive chart, and shows the exact Python code it executed.
3. Go to **Tab 2: Sandboxed Python Code Interpreter**:
   * Type: `print("Total rows:", len(df))` and click **Run Sandboxed Code**.
   * Notice the output executes securely inside an isolated Python runtime.
4. Go to **Tab 4: Predictive Machine Learning (AutoML)**:
   * Select a target column (e.g., `Churn` or `Annual_Salary`).
   * Click **"⚡ Run 5-Fold Cross-Validation AutoML Benchmark"**.
   * The platform trains multiple models (Random Forest, Gradient Boosting, Logistic Regression/Ridge) and displays a model accuracy leaderboard and feature importance ranking!

---

### 4️⃣ Step 4: Run Forensic Fraud Detection (Finance & Science Studios)
1. In the left navigation menu, click **💼 Finance & Science Studios**.
2. In the sidebar, select preset **"💼 SME Tally Financial Accounting & P&L Waterfall"**.
3. Go to **Tab 1: Tally Corporate P&L & Turnover Statements**:
   * View the corporate financial waterfall chart showing Gross Margin and Operating Profit.
4. Go to **Tab 2: Forensic Auditor & Anomaly Sentinel**:
   * View the **Benford's Law Digit Frequency Plot**.
   * The blue bars show actual transaction digits, and the red dotted line shows natural Benford expectation.
   * If an accountant fabricated invoices or capped amounts under ₹50,000 to evade approval thresholds, the platform flags the exact deviation digit and triggers a **High Sentinel Incident Report**!

---

### 5️⃣ Step 5: Download Boardroom Deliverables (Executive Reports & Decks)
1. In the left navigation menu, click **📥 Executive Reports & Decks**.
2. Go to **Tab 1: PowerPoint (.pptx) & 16:9 Decks**:
   * Click **"📊 Download PowerPoint Deck (.pptx)"**.
   * Open the file in Microsoft PowerPoint — you have an executive 10-slide widescreen presentation deck ready for the CEO or board of directors!
3. Go to **Tab 5: 🛡️ Governance & Compliance Certificate**:
   * Click **"📜 Download Compliance Certificate (.html)"**.
   * Open it in Chrome or Edge and press `Ctrl + P` to print or save as a sealed PDF. It contains a cryptographic **SHA-256 fingerprint** of your data, complete transformation lineage, and Sarbanes-Oxley (SOX) / GDPR compliance attestations!

---

## ❓ Frequently Asked Questions & Troubleshooting

### Q1: What if port 8501 is already in use?
* **Answer:** Run Streamlit on a different port:
  ```powershell
  streamlit run app.py --server.port=8502
  ```
  Then open `http://localhost:8502` in your browser.

### Q2: How do I stop the local server when I am done?
* **Answer:** Click on the terminal window running Streamlit and press `Ctrl + C`, then press `y` and `Enter`.

### Q3: Can I upload my own company data?
* **Answer:** Absolutely! In the sidebar, change **Source Mode** from *Benchmark Datasets* to **Upload File**. Drag and drop any `.csv` or multi-sheet `.xlsx` file.

### Q4: Is my uploaded data sent to any third party or cloud AI?
* **Answer:** **No.** Autonomous DA is built on a **Zero-Exfiltration Architecture**. All calculations, cleaning, machine learning, and slide generation run 100% locally on your computer inside memory. No tabular records are ever transmitted over the internet.

### Q5: What if I make a mistake while cleaning data?
* **Answer:** Click the button **"↺ Reset Dataset to Original"** in the sidebar, or go to **Executive Reports ➔ Tab 4: Checkpoints** to roll back to any saved stage snapshot instantly!

---
*Autonomous DA Enterprise &bull; Beginner User Manual v2.0 &bull; Ready for Evaluation*
