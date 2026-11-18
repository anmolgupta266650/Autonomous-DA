# 📘 Chapter 5: Enterprise Security, RBAC & Governance Framework

Enterprise data platforms are held to strict regulatory standards regarding data privacy, user authentication, role-based authorization, and tamper-evident audit trails. This chapter details how Autonomous DA implements enterprise-grade security and governance.

---

## 5.1 Authentication & Password Cryptography

User authentication is managed in `modules/db_manager.py` using **Salted SHA-256 Cryptographic Hashing**:

```python
# Password Hashing Mechanism in db_manager.py
salt = hashlib.sha256(username.lower().encode("utf-8")).hexdigest()[:16]
stored_hash = hashlib.sha256((salt + password).encode("utf-8")).hexdigest()
```

### Why Salted Hashing Matters:
1. **No Plaintext Passwords**: Passwords are never stored in plain text in the database (`data/projects.db`).
2. **Rainbow Table Immunity**: Salting appends a unique, deterministic prefix to each username before hashing, rendering pre-computed rainbow table dictionary attacks ineffective.

---

## 5.2 Enterprise Role-Based Access Control (RBAC) Matrix

Autonomous DA enforces strict authorization through **Role-Based Access Control (RBAC)**. In `app.py`, page routing is dynamically filtered based on the authenticated user's role:

| Enterprise Role | Seeded Login | Authorized Flagship Studios | Restricted / Hidden Pages |
| :--- | :--- | :--- | :--- |
| **👑 Administrator** | `admin` / `admin123` | **Full Platform Access**: Home, Data Studio, AI Hub, Finance & Science, Executive Export | None |
| **💼 CFO / Accountant** | `cfo_accountant` / `tally123` | Home, Data Studio, Finance & Science Studios, Executive Export | AI Intelligence Hub (AutoML & Code Sandbox hidden) |
| **🔬 Research Scientist** | `researcher` / `science123` | Home, Data Studio, AI Intelligence Hub, Finance & Science Studios (Research tab) | Tally P&L Statements & Corporate Accounting |
| **📊 Executive Viewer** | `executive` / `exec123` | Home, Data Studio (Read-only dashboards), Executive Reports & Decks | Data Cleaner, Feature Lab, AutoML Training, Code Interpreter |

### How RBAC Is Enforced in Streamlit:
In `app.py`, the master navigation bar evaluates `st.session_state.user['role']`. If an unprivileged user attempts to switch directly to a restricted page URL, the navigation guard intercepts the request and safely falls back to their authorized home screen with a warning notification:
```python
def safe_switch_page(target_page_path, fallback_title):
    try:
        st.switch_page(target_page_path)
    except Exception:
        st.warning("🔒 Access Restricted: Your role does not have permission to access this studio.")
```

---

## 5.3 Python Code Execution Sandbox Architecture

In `modules/data_copilot.py`, the **Sandboxed Python Code Interpreter** allows analysts and AI models to run Python code without exposing the host operating system to security vulnerabilities.

### Threat Mitigation Architecture:
1. **Restricted Global Scope**:
   * The `__builtins__` namespace is inspected and scrubbed of dangerous system calls:
     ```python
     safe_builtins = {
         k: v for k, v in builtins_dict.items()
         if k not in ["eval", "exec", "open", "__import__", "compile", "globals", "locals"]
     }
     ```
2. **Filesystem & Subprocess Isolation**:
   * Direct imports of `os`, `sys`, `subprocess`, `shutil`, `socket`, and `ctypes` are completely blocked.
   * A script cannot read local host files, cannot write to disk, and cannot open network sockets.
3. **In-Scope DataFrame Binding**:
   * The active DataFrame is passed as a cloned copy (`df.copy()`) alongside standard analytical libraries (`pd`, `np`, `px`, `go`).
4. **Buffered Stdout Capture**:
   * Console outputs (`print(...)`) are redirected to an in-memory `io.StringIO()` buffer and returned to the browser interface.

---

## 5.4 The Cryptographic SHA-256 Compliance Certificate

In banking, healthcare, and corporate governance, data analysts must provide **verifiable proof** that analytical reports were computed from authentic, unmanipulated records.

In `modules/report_exporter.py`, the platform generates a formal **Certificate of Data Governance & Analytical Integrity**:

### 1. Immutable State Fingerprint (SHA-256 Digest)
* When an audit is finalized, the active DataFrame is serialized to a deterministic byte sequence:
  $$\text{SHA-256 Digest} = \text{hashlib.sha256}(\text{df.to\_csv}().encode()).hexdigest()$$
* This 64-character hexadecimal string acts as an immutable tamper-evident seal. If even a single cell is altered, the SHA-256 hash changes completely.

### 2. Regulatory Alignment:
* **Sarbanes-Oxley (SOX) Section 404**: Ensures verifiable data provenance and transformation lineage without silent manual ledger tampering.
* **GDPR Article 30 (Records of Processing Activities)**: Proves zero remote data retention and local-only processing.

### 3. Print-Ready Certificate Deliverable:
* The certificate includes verified row/column counts, residual null counts, full audit trail lineage, operator signature lines, and official verification stamps.
* Formatted with CSS `@media print` rules: open in Google Chrome or Microsoft Edge and press `Ctrl + P` to export a clean, sealed PDF audit certificate.

---

## 5.5 Corporate Alert Webhook Simulator (Slack & Microsoft Teams)

To demonstrate how Autonomous DA integrates into modern corporate IT ecosystems, `modules/report_exporter.py` generates real-time JSON webhook payloads:

* **Forensic Sentinel Alert**: Triggered when Benford's Law anomaly deviations or round-number spikes exceed tolerance thresholds.
* **Executive Digest Snapshot**: Dispatched when an autonomous audit completes.
* **Formatted Block Kit / Adaptive Card**: Produces production-ready JSON payloads compatible with Slack Webhooks, Microsoft Teams Connectors, or PagerDuty event streams.

---
*Autonomous DA Enterprise &bull; Chapter 5 &bull; Security & Governance Framework*
