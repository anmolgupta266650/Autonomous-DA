import streamlit as st
import pandas as pd
from modules.common_ui import render_sidebar_data_controls, render_page_header
from modules.automl_engine import (
    detect_task_type, prepare_ml_data, train_and_evaluate_models
)

working_df = render_sidebar_data_controls()
render_page_header("🤖 Predictive AI & AutoML Studio", working_df)

st.markdown("### 🤖 Predictive Analytics & AutoML Studio")
st.caption("Benchmark classification and regression algorithms, inspect feature importances, and run What-If simulations.")

ml_col1, ml_col2 = st.columns([1, 2])

with ml_col1:
    st.markdown("##### ⚙️ Model Setup")
    target_choice = st.selectbox("Target Variable to Predict", working_df.columns.tolist(), help="The goal metric or category your model should learn to forecast.")
    inferred_task = detect_task_type(working_df[target_choice])
    st.info(f"Task Auto-Detected: **{inferred_task.upper()}**")

    selectable_features = [c for c in working_df.columns if c != target_choice]
    filtered_default_feats = [c for c in selectable_features if not c.lower().endswith("id")]
    chosen_features = st.multiselect("Predictor Features", selectable_features, default=filtered_default_feats, help="Select the input variables that influence the outcome.")

    train_trigger = st.button("🚀 Train & Benchmark Models", type="primary")

with ml_col2:
    if train_trigger:
        if not chosen_features:
            st.error("Please pick at least one feature.")
        else:
            with st.spinner("Training and benchmarking models..."):
                try:
                    X, y, task_t, t_enc, f_encs = prepare_ml_data(working_df, target_choice, chosen_features)
                    results_df, models_dict, best_m, diag_plot, feat_plot, test_data = train_and_evaluate_models(X, y, task_t)
                    
                    st.session_state.trained_ml = {
                        "results_df": results_df,
                        "models_dict": models_dict,
                        "best_model_name": best_m,
                        "diag_plot": diag_plot,
                        "feat_plot": feat_plot,
                        "task_type": task_t,
                        "target_col": target_choice,
                        "features": chosen_features,
                        "target_encoder": t_enc,
                        "feature_encoders": f_encs
                    }
                except Exception as e:
                    st.error(f"Training error: {str(e)}")

    if st.session_state.trained_ml:
        m_state = st.session_state.trained_ml
        st.markdown(f"##### 🏆 Benchmark Leaderboard ({m_state['task_type'].title()})")
        st.dataframe(m_state["results_df"], width="stretch")

        if m_state["feat_plot"]:
            st.plotly_chart(m_state["feat_plot"], width="stretch", key="automl_feat_importance_plot")
        if m_state["diag_plot"]:
            st.plotly_chart(m_state["diag_plot"], width="stretch", key="automl_diag_plot")

if st.session_state.trained_ml:
    st.markdown("---")
    st.markdown("#### 🔮 Interactive 'What-If' Prediction Simulator")
    st.caption("Adjust parameters below to see the best-performing model predict outcomes in real time.")

    m_state = st.session_state.trained_ml
    active_model = m_state["models_dict"][m_state["best_model_name"]]
    
    sim_cols = st.columns(min(len(m_state["features"]), 4))
    user_inputs = {}

    for idx, feat in enumerate(m_state["features"]):
        target_slot = sim_cols[idx % len(sim_cols)]
        with target_slot:
            if pd.api.types.is_numeric_dtype(working_df[feat]):
                f_min = float(working_df[feat].min()) if not pd.isna(working_df[feat].min()) else 0.0
                f_max = float(working_df[feat].max()) if not pd.isna(working_df[feat].max()) else 1.0
                if f_min >= f_max:
                    f_max = f_min + 1.0
                f_med = float(working_df[feat].median()) if not pd.isna(working_df[feat].median()) else f_min
                f_med = min(max(f_med, f_min), f_max)
                user_inputs[feat] = st.slider(feat, min_value=f_min, max_value=f_max, value=f_med)
            else:
                options = working_df[feat].dropna().unique().tolist()
                user_inputs[feat] = st.selectbox(feat, options)

    if st.button("⚡ Run Simulation", type="primary"):
        row_payload = pd.DataFrame([user_inputs])
        for feat, enc in m_state["feature_encoders"].items():
            if feat in row_payload.columns:
                val_str = str(row_payload[feat].iloc[0])
                if val_str in enc.classes_:
                    row_payload[feat] = enc.transform([val_str])[0]
                else:
                    row_payload[feat] = 0

        pred = active_model.predict(row_payload)[0]

        if m_state["task_type"] == "classification" and m_state["target_encoder"]:
            label = m_state["target_encoder"].inverse_transform([pred])[0]
            st.success(f"🎯 **Simulated Outcome for {m_state['target_col']}**: `{label}` (Algorithm: {m_state['best_model_name']})")
        else:
            st.success(f"🎯 **Simulated Outcome for {m_state['target_col']}**: `{pred:,.2f}` (Algorithm: {m_state['best_model_name']})")

