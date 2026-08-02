import sys
from pathlib import Path

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import httpx
import os

try:
    from dashboard.components.chunk_viewer import render_chunk_viewer
    from dashboard.components.styles import apply_master_theme
except ImportError:
    from components.chunk_viewer import render_chunk_viewer
    from components.styles import apply_master_theme

st.set_page_config(page_title="Interactive Query Inspector", page_icon="🔍", layout="wide")
apply_master_theme()

st.markdown('<div class="hero-title">🔍 Interactive Query Inspector</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Execute hybrid retrieval, neural reranking, and AI answer synthesis in real time</div>', unsafe_allow_html=True)

API_URL = os.getenv("API_URL", "http://localhost:8000")

with st.sidebar:
    st.header("⚡ Pipeline Controls")
    chunking_strategy = st.selectbox("Chunking Strategy", ["recursive", "fixed", "semantic"])
    hybrid_search = st.checkbox("Enable Hybrid Search (BM25 + Vector)", value=True)
    reranker = st.checkbox("Enable Cross-Encoder Reranker", value=True)
    query_rewriting = st.checkbox("Enable LLM Query Rewriting", value=True)

query = st.text_input("Enter your research question:", "What retrieval methods reduce hallucination in long-context RAG?")

if st.button("Run Query"):
    with st.spinner("Executing RAG Pipeline across arXiv Corpus..."):
        try:
            resp = httpx.post(
                f"{API_URL}/query",
                json={
                    "query": query,
                    "chunking_strategy": chunking_strategy,
                    "hybrid_search": hybrid_search,
                    "reranker": reranker,
                    "query_rewriting": query_rewriting,
                },
                timeout=120.0,
            )

            if resp.status_code == 200:
                data = resp.json()
                latency = data.get('latency_ms', 0)
                
                st.markdown(
                    f"""
                    <div style="display: flex; gap: 12px; margin-bottom: 20px; align-items: center;">
                        <span class="badge-green">Latency: {latency:.2f} ms</span>
                        <span class="badge-violet">Strategy: {chunking_strategy}</span>
                        <span class="badge-amber">Chunks Used: {len(data.get('chunks_used', []))}</span>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.markdown(
                    f"""
                    <div class="glass-card">
                        <h3 style="color: #6366F1; margin-top:0;">🤖 Generated Answer & Citations</h3>
                        <div style="font-size: 1.05rem; line-height: 1.7; color: #F3F4F6;">
                            {data.get("answer", "")}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

                st.subheader("📚 Retrieved & Reranked Context Chunks")
                render_chunk_viewer(data.get("chunks_used", []))

                # Feedback widget
                st.divider()
                st.subheader("Submit Query Feedback")
                col1, col2 = st.columns([1, 4])
                with col1:
                    rating = st.radio("Rating", ["👍 Thumbs Up (+1)", "👎 Thumbs Down (-1)"])
                with col2:
                    comment = st.text_input("Optional comment / feedback:")

                if st.button("Submit Feedback"):
                    rate_val = 1 if "Up" in rating else -1
                    chunk_ids = [c["chunk_id"] for c in data.get("chunks_used", [])]
                    httpx.post(
                        f"{API_URL}/feedback",
                        json={
                            "query": query,
                            "answer": data.get("answer", ""),
                            "chunks_used": chunk_ids,
                            "rating": rate_val,
                            "comments": comment,
                        },
                    )
                    st.success("Feedback submitted!")
            else:
                st.error(f"API Error {resp.status_code}: {resp.text}")
        except Exception as e:
            st.error(f"Could not connect to API server at {API_URL}: {e}")
