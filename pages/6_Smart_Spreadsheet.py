import streamlit as st
import pandas as pd
import numpy as np
from modules.common_ui import render_sidebar_data_controls, render_page_header
from modules.data_loader import get_dataset_metadata
from modules.db_manager import save_checkpoint

working_df = render_sidebar_data_controls()
render_page_header("📋 Smart Spreadsheet & Data Hub", working_df)

meta = get_dataset_metadata(working_df)

st.markdown("### 📋 Smart Spreadsheet & In-Browser Grid Editor")
st.caption("Direct in-browser cell editing, row insertion/deletion, high-speed vectorized search, and structural schema audit.")

tab_editor, tab_search = st.tabs(["✏️ Interactive Excel Grid Editor", "🔍 Vector Search & Column Schema"])

with tab_editor:
    st.markdown("##### ✏️ Direct Excel-Style Cell Editor")
    st.caption("Double-click any cell to modify values, click the '+' icon at the bottom of the grid to insert rows, or select rows and press 'Delete'.")

    edited_df = st.data_editor(
        st.session_state.df,
        num_rows="dynamic",
        use_container_width=True,
        height=460,
        key="spreadsheet_editor_grid"
    )

    ec1, ec2 = st.columns([2, 1])
    with ec1:
        commit_desc = st.text_input("Checkpoint Note", value="Manual row/cell edit via Interactive Spreadsheet", help="Descriptive note saved in SQLite audit log.")
    with ec2:
        st.write("")
        if st.button("💾 Commit Edits to Database Checkpoint", type="primary", use_container_width=True):
            st.session_state.df = edited_df.copy()
            st.session_state.current_stage = "Spreadsheet Manual Edit"
            save_checkpoint(st.session_state.project_id, "Spreadsheet Manual Edit", edited_df, commit_desc)
            st.session_state.last_action_msg = f"Saved spreadsheet changes ({len(edited_df):,} rows) as new checkpoint!"
            st.rerun()

with tab_search:
    st.markdown("##### 🔍 Vectorized Multi-Column Search")
    sc1, sc2 = st.columns([3, 1])
    with sc1:
        search_kw = st.text_input("Quick Keyword Filter", placeholder="Type any search term...", help="High-speed filter searching across all columns simultaneously.")
    with sc2:
        page_size = st.selectbox("Display Limit", [20, 50, 100, "All Records"], index=0)

    grid_df = working_df
    if search_kw:
        mask = np.logical_or.reduce([
            working_df[col].astype(str).str.contains(search_kw, case=False, na=False)
            for col in working_df.columns
        ])
        grid_df = working_df[mask]

    if page_size != "All Records":
        grid_df = grid_df.head(int(page_size))

    st.dataframe(grid_df, width="stretch", height=380)

    st.markdown("#### 📋 Column Schema & Health Breakdown")
    st.dataframe(meta.get("col_summary", pd.DataFrame()), width="stretch")

