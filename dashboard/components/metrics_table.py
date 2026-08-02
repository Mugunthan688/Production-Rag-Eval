import streamlit as st
import pandas as pd


def render_metrics_table(df: pd.DataFrame):
    if df.empty:
        st.info("No experiment results found yet. Run evaluation scripts or trigger from the API.")
        return

    st.dataframe(
        df.style.highlight_max(axis=0, color="#d4edda", subset=["Precision@5", "Recall@5", "MRR", "Faithfulness", "Relevance"]),
        use_container_width=True,
    )
