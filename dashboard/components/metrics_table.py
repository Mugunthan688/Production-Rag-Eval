import streamlit as st
import pandas as pd


def render_metrics_table(df: pd.DataFrame):
    if df.empty:
        st.info("No experiment results found yet. Run evaluation scripts or trigger from the API.")
        return

    metrics_cols = ["Precision@5", "Recall@5", "MRR", "Faithfulness", "Relevance"]
    available_subset = [col for col in metrics_cols if col in df.columns]

    styled_df = df.style
    if available_subset:
        styled_df = styled_df.highlight_max(axis=0, color="#d4edda", subset=available_subset)

    try:
        st.dataframe(styled_df, use_container_width=True)
    except TypeError:
        st.dataframe(styled_df, width="stretch")

