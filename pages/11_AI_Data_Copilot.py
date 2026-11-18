import streamlit as st
import pandas as pd
from modules.common_ui import render_sidebar_data_controls, render_page_header
from modules.data_copilot import ask_data_copilot, run_sandboxed_pandas_code

working_df = render_sidebar_data_controls()
render_page_header("💬 AI Data Copilot", working_df)

st.markdown("### 💬 AI Data Copilot 2.0 & Python Code Interpreter")
st.caption("Ask natural language questions or run sandboxed Python code to analyze, summarize, and visualize your data on the fly.")

copilot_tab1, copilot_tab2 = st.tabs(["💬 Conversational Copilot", "🧪 Python Code Interpreter Sandbox"])

# ==============================================================
# TAB 1: CONVERSATIONAL COPILOT
# ==============================================================
with copilot_tab1:
    if "copilot_messages" not in st.session_state:
        st.session_state.copilot_messages = [
            {
                "role": "assistant",
                "content": f"Hello! I am your AI Data Copilot. I'm connected to your active dataset with **{len(working_df):,} records** and **{len(working_df.columns)} columns**. What would you like to explore?",
                "data": None,
                "fig": None,
                "code": None
            }
        ]

    # Suggested Quick Prompts
    num_cols = working_df.select_dtypes(include=["number"]).columns.tolist()
    cat_cols = working_df.select_dtypes(include=["object", "category", "string"]).columns.tolist()

    suggested_queries = ["How many total records?"]
    if num_cols and cat_cols:
        suggested_queries.append(f"Top 5 {cat_cols[0]} by {num_cols[0]}")
        suggested_queries.append(f"Total {num_cols[0]} by {cat_cols[0]}")
        suggested_queries.append(f"Flag outliers in {num_cols[0]}")
    if len(num_cols) >= 2:
        suggested_queries.append(f"Correlation between {num_cols[0]} and {num_cols[1]}")

    st.markdown("##### 💡 Suggested Questions")
    s_cols = st.columns(len(suggested_queries[:4]))
    clicked_prompt = None
    for i, sq in enumerate(suggested_queries[:4]):
        with s_cols[i]:
            if st.button(sq, key=f"sq_btn_{i}", use_container_width=True):
                clicked_prompt = sq

    top_act_col, clr_col = st.columns([5, 1])
    with clr_col:
        if st.button("🧹 Clear Chat", key="copilot_clear_chat", use_container_width=True):
            st.session_state.copilot_messages = [
                {
                    "role": "assistant",
                    "content": f"Chat history cleared. Active dataset contains **{len(working_df):,} records**. How can I help?",
                    "data": None,
                    "fig": None,
                    "code": None
                }
            ]
            st.rerun()

    # Display chat history
    for idx, msg in enumerate(st.session_state.copilot_messages):
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])
            if msg.get("fig") is not None:
                st.plotly_chart(msg["fig"], width="stretch", key=f"copilot_chart_{idx}")
            if msg.get("data") is not None:
                st.dataframe(msg["data"], width="stretch", key=f"copilot_data_{idx}")
            if msg.get("code"):
                with st.expander("💻 View Generated Python Code", expanded=False):
                    st.code(msg["code"], language="python")

    # Chat input
    user_query = st.chat_input("Ask a question (e.g. 'Who are top 5 clients by sales?', 'Flag outliers in profit', 'Show monthly trend')...")

    prompt_to_run = clicked_prompt or user_query

    if prompt_to_run:
        st.session_state.copilot_messages.append({"role": "user", "content": prompt_to_run})
        copilot_res = ask_data_copilot(working_df, prompt_to_run)
        st.session_state.copilot_messages.append({
            "role": "assistant",
            "content": copilot_res["answer"],
            "data": copilot_res.get("data"),
            "fig": copilot_res.get("fig"),
            "code": copilot_res.get("generated_code")
        })
        st.rerun()

# ==============================================================
# TAB 2: PYTHON CODE INTERPRETER SANDBOX
# ==============================================================
with copilot_tab2:
    st.markdown("##### 🧪 Advanced Python Code Interpreter (Isolated Execution)")
    st.caption("Write and execute custom Pandas, NumPy, or Plotly code against your active `df`. Set `result = df...` or `fig = px...` to render interactive outputs.")

    default_code = (
        "# Example: Group and calculate summary statistics\n"
        "numeric_cols = df.select_dtypes(include=['number']).columns\n"
        "if len(numeric_cols) > 0:\n"
        "    col = numeric_cols[0]\n"
        "    result = df.describe().T[['mean', 'std', 'min', '50%', 'max']]\n"
        "    fig = px.histogram(df, x=col, title=f'Distribution of {col}', nbins=25)\n"
        "    fig.update_layout(template='plotly_dark')\n"
        "else:\n"
        "    result = df.head(10)\n"
    )

    code_input = st.text_area("Python Script", value=default_code, height=180, key="sandbox_code_input")

    if st.button("⚡ Run Code in Sandbox", type="primary", key="run_sandbox_btn"):
        exec_res = run_sandboxed_pandas_code(working_df, code_input)

        if exec_res["error"]:
            st.error(f"Execution Error: {exec_res['error']}")
        else:
            st.success("Execution completed successfully!")
            if exec_res["stdout"]:
                with st.expander("📜 Standard Output (Console)", expanded=True):
                    st.text(exec_res["stdout"])

            if exec_res["fig"] is not None:
                st.plotly_chart(exec_res["fig"], width="stretch", key="sandbox_res_fig")

            if exec_res["data"] is not None:
                st.dataframe(exec_res["data"], width="stretch", key="sandbox_res_df")
