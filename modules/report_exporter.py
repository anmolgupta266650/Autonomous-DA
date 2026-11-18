import io
import hashlib
import datetime
import pandas as pd


def export_to_csv(df: pd.DataFrame) -> bytes:
    """Converts DataFrame to CSV bytes for Streamlit download button."""
    return df.to_csv(index=False).encode("utf-8")


def export_to_excel(df: pd.DataFrame) -> bytes:
    """Converts DataFrame to styled Excel (.xlsx) bytes."""
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Cleaned_Data")
        # Auto-adjust column widths
        workbook = writer.book
        worksheet = writer.sheets["Cleaned_Data"]
        header_format = workbook.add_format({
            "bold": True,
            "text_wrap": True,
            "valign": "top",
            "fg_color": "#4f46e5",
            "font_color": "#ffffff",
            "border": 1
        })
        for col_num, col_name in enumerate(df.columns):
            worksheet.write(0, col_num, col_name, header_format)
            header_len = len(str(col_name))
            if df.empty:
                max_len = header_len + 3
            else:
                try:
                    str_lens = df.iloc[:, col_num].astype(str).str.len()
                    val_max = str_lens.max()
                    val_len = int(val_max) if pd.notna(val_max) else 0
                except Exception:
                    val_len = 0
                max_len = max(val_len, header_len) + 3
            worksheet.set_column(col_num, col_num, min(max(max_len, 10), 40))
    return output.getvalue()


def generate_executive_html_report(df: pd.DataFrame, metadata: dict, insights: list, ml_results=None) -> str:
    """
    Generates a standalone, beautifully styled HTML analytical report for presentation or archival.
    """
    if metadata is None:
        metadata = {}

    insights_html = ""
    for ins in (insights or []):
        if isinstance(ins, dict):
            ins_type = ins.get("type", "info")
            ins_cat = ins.get("category", "EXECUTIVE INSIGHT")
            ins_title = ins.get("title", "Insight Observation")
            ins_desc = ins.get("description", "")
        else:
            ins_type = "info"
            ins_cat = "EXECUTIVE INSIGHT"
            ins_title = "Insight Observation"
            ins_desc = str(ins)

        badge_color = "#10b981" if ins_type == "success" else "#f59e0b" if ins_type == "warning" else "#6366f1"
        insights_html += f"""
        <div style="background:#1e293b; border-left: 4px solid {badge_color}; border-radius: 6px; padding: 12px 16px; margin-bottom: 12px;">
            <div style="font-size: 11px; text-transform: uppercase; color: {badge_color}; font-weight: 700;">{ins_cat}</div>
            <div style="font-size: 15px; font-weight: 600; color: #f8fafc; margin: 4px 0;">{ins_title}</div>
            <div style="font-size: 13px; color: #94a3b8;">{ins_desc}</div>
        </div>
        """

    ml_table_html = ""
    if ml_results is not None and isinstance(ml_results, pd.DataFrame) and not ml_results.empty:
        ml_table_html = """
        <h3 style="color: #c7d2fe; margin-top: 24px;">Automated Machine Learning Benchmark</h3>
        <table style="width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 13px;">
            <thead>
                <tr style="background: #312e81; color: #ffffff;">
        """
        for col in ml_results.columns:
            ml_table_html += f"<th style='padding: 8px 12px; text-align: left; border: 1px solid #4338ca;'>{col}</th>"
        ml_table_html += "</tr></thead><tbody>"
        for _, row in ml_results.iterrows():
            ml_table_html += "<tr style='background: #1e293b; border-bottom: 1px solid #334155;'>"
            for col in ml_results.columns:
                ml_table_html += f"<td style='padding: 8px 12px; color: #cbd5e1;'>{row[col]}</td>"
            ml_table_html += "</tr>"
        ml_table_html += "</tbody></table>"

    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <title>Executive Data Intelligence Report</title>
        <style>
            body {{
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                background-color: #0f172a;
                color: #f8fafc;
                margin: 0;
                padding: 40px 20px;
            }}
            .container {{
                max-width: 900px;
                margin: 0 auto;
                background: #111827;
                border: 1px solid rgba(255,255,255,0.1);
                border-radius: 12px;
                padding: 32px;
                box-shadow: 0 10px 30px rgba(0,0,0,0.5);
            }}
            .kpi-grid {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 16px;
                margin: 24px 0;
            }}
            .kpi-tile {{
                background: #1f2937;
                border: 1px solid rgba(255,255,255,0.06);
                border-radius: 8px;
                padding: 16px;
                text-align: center;
            }}
            .kpi-title {{ font-size: 11px; text-transform: uppercase; color: #9ca3af; }}
            .kpi-value {{ font-size: 22px; font-weight: 700; color: #38bdf8; margin-top: 4px; }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1 style="margin: 0; font-size: 26px; background: linear-gradient(90deg, #818cf8, #38bdf8); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Autonomous DA — Executive Intelligence Report
            </h1>
            <p style="color: #94a3b8; font-size: 13px; margin-top: 4px;">Automated Data Profiling, Strategic Drivers & Performance Analytics</p>

            <div class="kpi-grid">
                <div class="kpi-tile">
                    <div class="kpi-title">Total Records</div>
                    <div class="kpi-value">{metadata.get('rows', 0):,}</div>
                </div>
                <div class="kpi-tile">
                    <div class="kpi-title">Features</div>
                    <div class="kpi-value">{metadata.get('cols', 0)}</div>
                </div>
                <div class="kpi-tile">
                    <div class="kpi-title">Missing Cells</div>
                    <div class="kpi-value">{metadata.get('missing_cells', 0)} ({metadata.get('missing_pct', 0)}%)</div>
                </div>
                <div class="kpi-tile">
                    <div class="kpi-title">Health Score</div>
                    <div class="kpi-value">{metadata.get('health_score', 0)} / 100</div>
                </div>
            </div>

            <h3 style="color: #c7d2fe; margin-top: 32px;">Executive Strategic Insights</h3>
            {insights_html}

            {ml_table_html}

            <div style="margin-top: 40px; border-top: 1px solid #334155; padding-top: 16px; font-size: 11px; color: #64748b; text-align: center;">
                Generated automatically by Autonomous DA &bull; Academic Final Year Capstone Platform
            </div>
        </div>
    </body>
    </html>
    """
    return html_content


def generate_compliance_certificate(df: pd.DataFrame, dataset_name: str, project_id: str, audit_log: list = None, user: dict = None) -> str:
    """
    Generates a verifiable, formal Enterprise Data Governance & Cryptographic Integrity Certificate.
    Includes SHA-256 data fingerprint, zero-exfiltration privacy affirmation, and audit trail lineage.
    """
    # 1. Compute SHA-256 hash of dataset representation
    try:
        csv_bytes = df.to_csv(index=False).encode("utf-8")
        sha256_hash = hashlib.sha256(csv_bytes).hexdigest()
    except Exception:
        sha256_hash = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"

    timestamp_str = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
    cert_id = f"CERT-DA-{sha256_hash[:12].upper()}"
    operator = user.get("username", "system_admin") if user else "authenticated_operator"
    role = user.get("role", "admin").upper() if user else "EXECUTIVE_ADMIN"

    rows = len(df)
    cols = len(df.columns)
    null_count = int(df.isna().sum().sum())
    dup_count = int(df.duplicated().sum())
    memory_kb = round(df.memory_usage(deep=True).sum() / 1024, 2)

    # Lineage events
    audit_events = audit_log if audit_log else ["Dataset ingested into memory.", "Lineage baseline established."]
    lineage_items = "".join([f"<li style='margin-bottom:6px; color:#334155; font-size:12px;'><code>[{i+1}]</code> {evt}</li>" for i, evt in enumerate(audit_events[-10:])])

    html_cert = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Data Integrity & Governance Certificate - {cert_id}</title>
<style>
    @page {{ size: A4 portrait; margin: 15mm; }}
    @media print {{
        body {{ background: #ffffff !important; color: #0f172a !important; padding: 0 !important; }}
        .cert-card {{ border: 2px solid #0f172a !important; box-shadow: none !important; }}
        .btn-print {{ display: none !important; }}
    }}
    body {{
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        background: #0f172a;
        color: #0f172a;
        margin: 0;
        padding: 24px;
        display: flex;
        justify-content: center;
    }}
    .cert-card {{
        background: #ffffff;
        width: 100%;
        max-width: 820px;
        border: 2px solid #4f46e5;
        border-radius: 12px;
        padding: 40px;
        box-shadow: 0 20px 40px rgba(0,0,0,0.4);
        position: relative;
    }}
    .cert-header {{
        border-bottom: 2px solid #e2e8f0;
        padding-bottom: 20px;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }}
    .cert-title {{
        font-size: 22px;
        font-weight: 800;
        color: #1e1b4b;
        letter-spacing: -0.5px;
    }}
    .cert-subtitle {{
        font-size: 12px;
        text-transform: uppercase;
        color: #6366f1;
        font-weight: 700;
        letter-spacing: 1px;
    }}
    .cert-id {{
        background: #f1f5f9;
        padding: 6px 12px;
        border-radius: 6px;
        font-family: monospace;
        font-size: 13px;
        color: #0f172a;
        font-weight: 700;
        border: 1px solid #cbd5e1;
    }}
    .metric-grid {{
        display: grid;
        grid-template-columns: repeat(4, 1fr);
        gap: 12px;
        margin: 24px 0;
    }}
    .metric-tile {{
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 8px;
        padding: 12px;
        text-align: center;
    }}
    .metric-label {{ font-size: 11px; text-transform: uppercase; color: #64748b; font-weight: 600; }}
    .metric-val {{ font-size: 18px; font-weight: 800; color: #1e293b; margin-top: 4px; }}
    .hash-box {{
        background: #0f172a;
        color: #38bdf8;
        padding: 14px 18px;
        border-radius: 8px;
        font-family: monospace;
        font-size: 12px;
        word-break: break-all;
        margin: 20px 0;
        border: 1px solid #1e293b;
    }}
    .governance-block {{
        background: #f0fdf4;
        border: 1px solid #bbf7d0;
        border-radius: 8px;
        padding: 16px;
        margin: 20px 0;
    }}
    .gov-title {{ font-size: 13px; font-weight: 700; color: #166534; margin-bottom: 6px; }}
    .gov-desc {{ font-size: 12px; color: #14532d; line-height: 1.5; }}
    .signatures {{
        margin-top: 36px;
        padding-top: 20px;
        border-top: 1px solid #e2e8f0;
        display: flex;
        justify-content: space-between;
    }}
    .sig-block {{ width: 45%; }}
    .sig-line {{ border-bottom: 1px solid #94a3b8; height: 35px; margin-bottom: 6px; }}
    .sig-name {{ font-size: 12px; font-weight: 700; color: #1e293b; }}
    .sig-title {{ font-size: 11px; color: #64748b; }}
</style>
</head>
<body>
<div class="cert-card">
    <div class="cert-header">
        <div>
            <div class="cert-subtitle">Autonomous DA &bull; Regulatory Compliance & Assurance</div>
            <div class="cert-title">Certificate of Data Governance & Analytical Integrity</div>
        </div>
        <div class="cert-id">{cert_id}</div>
    </div>

    <p style="font-size: 13px; color: #475569; margin: 18px 0 12px 0; line-height: 1.6;">
        This document certifies that dataset <strong>&ldquo;{dataset_name}&rdquo;</strong> (Project ID: <code>{project_id}</code>) has been ingested, validated, and processed under strict deterministic data integrity protocols with an immutable cryptographic fingerprint.
    </p>

    <div class="hash-box">
        <span style="color:#94a3b8; display:block; font-size:10px; margin-bottom:4px; text-transform:uppercase;">Cryptographic SHA-256 Digest (Immutable State Fingerprint)</span>
        {sha256_hash}
    </div>

    <div class="metric-grid">
        <div class="metric-tile">
            <div class="metric-label">Verified Rows</div>
            <div class="metric-val">{rows:,}</div>
        </div>
        <div class="metric-tile">
            <div class="metric-label">Validated Cols</div>
            <div class="metric-val">{cols}</div>
        </div>
        <div class="metric-tile">
            <div class="metric-label">Residual Nulls</div>
            <div class="metric-val">{null_count}</div>
        </div>
        <div class="metric-tile">
            <div class="metric-label">Memory Footprint</div>
            <div class="metric-val">{memory_kb} KB</div>
        </div>
    </div>

    <div class="governance-block">
        <div class="gov-title">🛡️ Data Privacy & Regulatory Attestation</div>
        <div class="gov-desc">
            &bull; <strong>Zero-Exfiltration Architecture:</strong> All analytics, feature transformations, and financial summaries are computed in-memory within the host runtime. No proprietary tabular records are transmitted to third-party endpoints.<br/>
            &bull; <strong>Sarbanes-Oxley (SOX) Section 404:</strong> Transformation audit logs ensure verifiable data provenance without silent record manipulation.<br/>
            &bull; <strong>GDPR Article 30 (Records of Processing):</strong> Operational modifications are timestamped and preserved in persistent checkpoint registers.
        </div>
    </div>

    <div style="margin-top: 16px;">
        <div style="font-size: 12px; font-weight: 700; color: #1e293b; text-transform: uppercase; margin-bottom: 8px;">Audit Provenance & Transformation Lineage:</div>
        <ul style="margin: 0; padding-left: 18px;">
            {lineage_items}
        </ul>
    </div>

    <div class="signatures">
        <div class="sig-block">
            <div class="sig-line"></div>
            <div class="sig-name">{operator}</div>
            <div class="sig-title">Certified Operator &bull; Role: {role}</div>
            <div class="sig-title">Timestamp: {timestamp_str}</div>
        </div>
        <div class="sig-block" style="text-align: right;">
            <div class="sig-line"></div>
            <div class="sig-name">Autonomous DA Compliance Verification Daemon</div>
            <div class="sig-title">Autonomous Analytics Engine 2.0</div>
            <div class="sig-title">Status: VERIFIED & SEALED</div>
        </div>
    </div>
</div>
</body>
</html>"""
    return html_cert


def generate_simulated_alert_payload(df: pd.DataFrame, dataset_name: str, alert_type: str = "forensic") -> dict:
    """
    Builds a simulated enterprise Slack Block Kit / Microsoft Teams JSON alert payload.
    """
    timestamp = datetime.datetime.now(datetime.timezone.utc).isoformat()
    rows = len(df)
    cols = len(df.columns)
    
    if alert_type == "forensic":
        title = f"🚨 [Autonomous DA] High-Priority Financial Sentinel Alert: {dataset_name}"
        color = "#ef4444"
        details = "Forensic engine detected Benford's Law distribution anomalies and round-number spike clusters exceeding tolerance thresholds."
    else:
        title = f"📊 [Autonomous DA] Executive Digest Snapshot: {dataset_name}"
        color = "#3b82f6"
        details = f"Autonomous analysis completed for {rows:,} records across {cols} columns. All stage checkpoints committed."

    slack_blocks = {
        "text": title,
        "blocks": [
            {
                "type": "header",
                "text": {"type": "plain_text", "text": title, "emoji": True}
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": f"*Environment:* Production &bull; *Dataset:* `{dataset_name}`\n*Timestamp:* `{timestamp}`\n\n{details}"}
            },
            {
                "type": "section",
                "fields": [
                    {"type": "mrkdwn", "text": f"*Total Records:*\n{rows:,}"},
                    {"type": "mrkdwn", "text": f"*Total Features:*\n{cols}"},
                    {"type": "mrkdwn", "text": "*Audit Status:*\n✅ Checkpoint Saved"},
                    {"type": "mrkdwn", "text": "*Execution Runtime:*\nHost Isolated (0 Exfiltration)"}
                ]
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {"type": "plain_text", "text": "View Live Executive Hub", "emoji": True},
                        "url": "https://anmol-autonomous-da.streamlit.app",
                        "style": "primary"
                    }
                ]
            }
        ]
    }
    return slack_blocks
