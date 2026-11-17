import streamlit as st
import pandas as pd
from modules.common_ui import render_sidebar_data_controls, render_page_header
from modules.db_manager import (
    list_projects, save_checkpoint, list_checkpoints, load_checkpoint
)

working_df = render_sidebar_data_controls()
render_page_header("💾 Project Database & Checkpoints", working_df)

st.markdown("### 💾 Persistent Relational Database & Pipeline Checkpoints")
st.caption("All datasets, pipeline checkpoints, and research papers are securely stored in a persistent SQLite database.")

db_c1, db_c2 = st.columns([1, 2])
with db_c1:
    st.markdown("##### 📌 Save Current Pipeline Stage")
    stage_name_input = st.text_input("Stage Name", value=f"Transformed Step {len(list_checkpoints(st.session_state.project_id)) + 1}", help="A clear descriptive name for this state snapshot.")
    stage_desc_input = st.text_area("Stage Description / Notes", placeholder="e.g. Imputed null values and normalized sales column")
    if st.button("💾 Commit Stage to Database", type="primary"):
        c_id = save_checkpoint(st.session_state.project_id, stage_name_input, working_df, stage_desc_input)
        st.session_state.current_stage = stage_name_input
        st.session_state.last_action_msg = f"Saved checkpoint #{c_id} ('{stage_name_input}') to persistent database!"
        st.rerun()

with db_c2:
    st.markdown("##### 📜 Project Checkpoint History")
    checkpoints = list_checkpoints(st.session_state.project_id)
    if checkpoints:
        cp_df = pd.DataFrame(checkpoints)
        st.dataframe(cp_df[["id", "stage_name", "description", "row_count", "col_count", "created_at"]], width="stretch")
        
        cp_labels = [f"#{c['id']} {c['stage_name']} ({c['row_count']} rows)" for c in checkpoints]
        sel_cp = st.selectbox("Select Checkpoint to Restore", cp_labels, help="Pick any historical stage to roll back without losing work.")
        if st.button("⏮️ Restore Selected Checkpoint"):
            sel_id = int(sel_cp.split()[0].replace("#", ""))
            cp_data = load_checkpoint(sel_id)
            if cp_data:
                restored_df, r_meta = cp_data
                st.session_state.df = restored_df.copy()
                st.session_state.current_stage = r_meta["stage_name"]
                st.session_state.last_action_msg = f"Successfully rolled back to Stage: '{r_meta['stage_name']}'!"
                st.rerun()
    else:
        st.info("No checkpoints saved yet for this project.")

st.markdown("---")
st.markdown("##### 🗄️ Database Projects Overview")
projs = list_projects()
if projs:
    p_df = pd.DataFrame(projs)
    st.dataframe(p_df[["id", "name", "current_stage", "created_at", "updated_at"]], width="stretch")

