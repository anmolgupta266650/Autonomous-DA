import streamlit as st
import pandas as pd
from modules.common_ui import render_sidebar_data_controls, render_page_header
from modules.report_exporter import export_to_csv, export_to_excel, generate_executive_html_report
from modules.presentation_generator import generate_executive_presentation_deck
from modules.pptx_generator import generate_executive_pptx_deck
from modules.tally_finance import detect_financial_columns, compute_tally_financial_metrics
from modules.business_insights import generate_executive_insights
from modules.data_loader import get_dataset_metadata
from modules.db_manager import list_checkpoints, load_checkpoint

working_df = render_sidebar_data_controls()
render_page_header("📥 Executive Reports & Decks", working_df)

meta = get_dataset_metadata(working_df)
insights_list = generate_executive_insights(working_df)
auto_fin = detect_financial_columns(working_df)
fin_metrics = compute_tally_financial_metrics(working_df, rev_col=auto_fin["revenue"], exp_col=auto_fin["expense"])

st.markdown("### 📥 Executive Reports, Decks & Governance Center")
st.caption("Generate presentation-ready 10-slide PowerPoint (.pptx) decks, standalone executive HTML briefings, styled Excel sheets, and inspect data lineage checkpoints.")

tab_pptx, tab_html, tab_data, tab_checkpoints = st.tabs([
    "📑 PowerPoint (.pptx) & 16:9 Decks",
    "🌐 Executive HTML Intelligence Report",
    "📑 Styled Excel (.xlsx) & CSV Export",
    "💾 Data Lineage & Audit Checkpoints"
])

# ==============================================================
# TAB 1: POWERPOINT & PRESENTATION DECKS
# ==============================================================
with tab_pptx:
    st.markdown("##### 📑 1-Click Executive Presentation Slide Decks")
    st.caption("Generate a professional 10-slide widescreen presentation deck in native Microsoft PowerPoint (.pptx) or standalone web format.")

    try:
        pptx_bytes = generate_executive_pptx_deck(
            df=working_df,
            dataset_name=st.session_state.dataset_name,
            meta=meta,
            fin_metrics=fin_metrics,
            insights=insights_list
        )
    except Exception:
        pptx_bytes = None

    deck_html = generate_executive_presentation_deck(
        df=working_df,
        dataset_name=st.session_state.dataset_name,
        meta=meta,
        fin_metrics=fin_metrics,
        insights=insights_list
    )

    pd1, pd2 = st.columns(2)
    with pd1:
        if pptx_bytes:
            st.download_button(
                label="📊 Download PowerPoint Deck (.pptx)",
                data=pptx_bytes,
                file_name=f"{st.session_state.project_id}_Executive_Deck.pptx",
                mime="application/vnd.openxmlformats-officedocument.presentationml.presentation",
                type="primary",
                key="btn_dl_pptx_hub"
            )
            st.caption("✅ 100% editable in PowerPoint, Keynote & Google Slides.")
        else:
            st.warning("Could not build PowerPoint deck.")

    with pd2:
        st.download_button(
            label="🌐 Download Web Slide Deck (.html)",
            data=deck_html.encode("utf-8"),
            file_name=f"{st.session_state.project_id}_SlideDeck.html",
            mime="text/html",
            key="btn_dl_html_hub"
        )
        st.caption("💡 Open HTML and press `Ctrl+P -> Save as PDF` for instant PDF presentation.")

    with st.expander("👁️ Live Slide Deck Preview", expanded=False):
        st.components.v1.html(deck_html, height=580, scrolling=True)


# ==============================================================
# TAB 2: EXECUTIVE HTML REPORT
# ==============================================================
with tab_html:
    st.markdown("##### 🌐 Executive HTML Intelligence Report")
    st.caption("Standalone self-contained HTML report with KPI scorecards, data health index, automated insights, and benchmark charts.")

    ml_bench_table = st.session_state.trained_ml["results_df"] if st.session_state.trained_ml else None
    html_rep = generate_executive_html_report(working_df, meta, insights_list, ml_bench_table)

    st.download_button(
        label="⬇️ Download Executive HTML Report (.html)",
        data=html_rep.encode("utf-8"),
        file_name=f"{st.session_state.project_id}_Executive_Report.html",
        mime="text/html",
        type="primary",
        key="btn_dl_html_rep_hub"
    )

    with st.expander("👁️ Live Report Preview", expanded=False):
        st.components.v1.html(html_rep, height=580, scrolling=True)


# ==============================================================
# TAB 3: EXCEL & CSV EXPORT
# ==============================================================
with tab_data:
    st.markdown("##### 📑 Formatted Spreadsheets & Raw Delimited Data")
    ex1, ex2 = st.columns(2)
    with ex1:
        st.markdown("###### Styled Excel (.xlsx)")
        st.caption("Multi-column formatted workbook with styled headers and automatic column widths.")
        try:
            excel_data = export_to_excel(working_df)
            st.download_button(
                label="⬇️ Download Excel (.xlsx)",
                data=excel_data,
                file_name=f"{st.session_state.project_id}_Dataset.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                key="btn_dl_excel_hub"
            )
        except Exception as exc:
            st.warning(f"Excel export: {exc}")

    with ex2:
        st.markdown("###### Raw CSV (.csv)")
        st.caption("Clean UTF-8 comma-separated format for database pipelines and custom code.")
        csv_data = export_to_csv(working_df)
        st.download_button(
            label="⬇️ Download CSV (.csv)",
            data=csv_data,
            file_name=f"{st.session_state.project_id}_Dataset.csv",
            mime="text/csv",
            key="btn_dl_csv_hub"
        )


# ==============================================================
# TAB 4: DATA LINEAGE & CHECKPOINTS
# ==============================================================
with tab_checkpoints:
    st.markdown("##### 💾 Immutable Data Lineage & Stage Checkpoints")
    st.caption("Inspect audit logs, review pipeline history, and restore previous dataset checkpoints.")

    checkpoints = list_checkpoints(st.session_state.project_id)
    if checkpoints:
        st.write(f"Found **{len(checkpoints)} historical stage checkpoints** for project `{st.session_state.project_id}`.")
        chk_df = pd.DataFrame([
            {
                "Stage": c.get("stage_name"),
                "Description": c.get("notes"),
                "Rows": c.get("rows"),
                "Columns": c.get("columns"),
                "Timestamp": c.get("created_at")
            }
            for c in checkpoints
        ])
        st.dataframe(chk_df, width="stretch", hide_index=True)

        st.markdown("###### Rollback to Previous Checkpoint")
        chk_options = {f"{c['stage_name']} ({c['created_at']})": c["id"] for c in checkpoints}
        sel_chk_label = st.selectbox("Select Checkpoint Snapshot", list(chk_options.keys()), key="rollback_chk_sel")
        if st.button("↺ Restore Selected Snapshot", type="primary", key="btn_restore_chk"):
            res = load_checkpoint(chk_options[sel_chk_label])
            if res:
                loaded_df, meta_c = res
                st.session_state.df = loaded_df.copy()
                st.session_state.raw_df = loaded_df.copy()
                st.session_state.current_stage = meta_c.get("stage_name", "Restored")
                st.session_state.last_action_msg = f"Restored checkpoint: {meta_c.get('stage_name')}"
                st.rerun()
    else:
        st.info("No checkpoints recorded yet for the current project.")
