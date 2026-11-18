import io
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
