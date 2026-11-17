import streamlit as st
import pandas as pd
from modules.common_ui import render_sidebar_data_controls, render_page_header
from modules.report_exporter import export_to_csv, export_to_excel, generate_executive_html_report
from modules.presentation_generator import generate_executive_presentation_deck
from modules.tally_finance import detect_financial_columns, compute_tally_financial_metrics
from modules.business_insights import generate_executive_insights
from modules.data_loader import get_dataset_metadata

working_df = render_sidebar_data_controls()
render_page_header("📥 Export & Reports Center", working_df)

meta = get_dataset_metadata(working_df)

st.markdown("### 📥 Export & Intelligence Reporting Center")
st.caption("Download cleaned datasets, standalone HTML briefings, executive presentation slide decks, and APA research manuscripts.")

e1, e2, e3, e4 = st.columns(4)

with e1:
    st.markdown("##### 📄 Cleaned CSV")
    st.caption("Standard delimited format for database migration or custom Python pipelines.")
    csv_data = export_to_csv(working_df)
    if st.download_button(
        label="⬇️ Download CSV",
        data=csv_data,
        file_name=f"{st.session_state.project_id}_Cleaned.csv",
        mime="text/csv"
    ):
        st.session_state.reports_exported_count += 1

with e2:
    st.markdown("##### 📑 Styled Excel (.xlsx)")
    st.caption("Formatted Excel workbook with styled table headers and automatic column widths.")
    try:
        excel_data = export_to_excel(working_df)
        if st.download_button(
            label="⬇️ Download Excel (.xlsx)",
            data=excel_data,
            file_name=f"{st.session_state.project_id}_Dataset.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ):
            st.session_state.reports_exported_count += 1
    except Exception as exc:
        st.warning(f"Could not generate Excel export: {exc}")

with e3:
    st.markdown("##### 🌐 Executive HTML Report")
    st.caption("Complete standalone HTML report containing KPIs, schema health, and business insights.")
    ml_bench_table = st.session_state.trained_ml["results_df"] if st.session_state.trained_ml else None
    insights_list = generate_executive_insights(working_df)
    html_rep = generate_executive_html_report(working_df, meta, insights_list, ml_bench_table)
    if st.download_button(
        label="⬇️ Download Executive Report (.html)",
        data=html_rep.encode("utf-8"),
        file_name=f"{st.session_state.project_id}_Executive_Report.html",
        mime="text/html"
    ):
        st.session_state.reports_exported_count += 1

with e4:
    st.markdown("##### 📝 Academic APA Paper")
    st.caption("Publication-ready empirical manuscript formatted to APA 7th Edition.")
    if st.session_state.active_research_paper:
        if st.download_button(
            label="⬇️ Download APA Paper (.md)",
            data=st.session_state.active_research_paper,
            file_name=f"{st.session_state.project_id}_Research_Paper.md",
            mime="text/markdown"
        ):
            st.session_state.reports_exported_count += 1
    else:
        st.info("Synthesize paper in the 'Scientific Research' page first.")

st.markdown("---")

# Executive Presentation Slide Deck (16:9)
st.markdown("### 📑 1-Click Executive Presentation Slide Deck (16:9)")
st.caption("Generates a standalone, presentation-ready 16:9 slide deck in HTML/CSS. Press Ctrl+P (or Cmd+P) in your browser to print directly to PDF with clean slide breaks.")

auto_fin = detect_financial_columns(working_df)
fin_metrics = compute_tally_financial_metrics(working_df, rev_col=auto_fin["revenue"], exp_col=auto_fin["expense"])
deck_html = generate_executive_presentation_deck(
    df=working_df,
    dataset_name=st.session_state.dataset_name,
    meta=meta,
    fin_metrics=fin_metrics,
    insights=insights_list
)

sd1, sd2 = st.columns([2, 1])
with sd1:
    st.download_button(
        label="⬇️ Download Executive Slide Deck (.html)",
        data=deck_html.encode("utf-8"),
        file_name=f"{st.session_state.project_id}_SlideDeck.html",
        mime="text/html",
        type="primary"
    )
with sd2:
    st.caption("💡 Open the downloaded HTML file in Chrome/Edge and press **Ctrl+P -> Destination: Save as PDF** to generate an executive PDF presentation.")

with st.expander("👁️ Live Slide Deck Preview", expanded=False):
    st.components.v1.html(deck_html, height=620, scrolling=True)

