from typing import List, Dict, Any
import streamlit as st


def render_chunk_viewer(chunks: List[Dict[str, Any]]):
    if not chunks:
        st.info("No context chunks retrieved.")
        return

    for idx, chunk in enumerate(chunks, 1):
        score = chunk.get('score', 0.0)
        paper_id = chunk.get('paper_id', 'Unknown')
        chunk_id = chunk.get('chunk_id', 'Unknown')
        text_snippet = chunk.get('text', '')

        with st.expander(f"📄 Chunk #{idx} — Paper [{paper_id}] | Reranker Score: {score:.4f}"):
            st.markdown(
                f"""
                <div style="display: flex; gap: 10px; margin-bottom: 8px;">
                    <span class="badge-violet">Paper ID: {paper_id}</span>
                    <span class="badge-green">Score: {score:.4f}</span>
                    <span class="badge-amber">Chunk: {chunk_id}</span>
                </div>
                """,
                unsafe_allow_html=True,
            )
            st.markdown(f"```text\n{text_snippet}\n```")
