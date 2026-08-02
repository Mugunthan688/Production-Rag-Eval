import sys
from pathlib import Path

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
try:
    from dashboard.components.styles import apply_master_theme
except ImportError:
    from components.styles import apply_master_theme

st.set_page_config(
    page_title="Production RAG System | Deep Research AI",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)

apply_master_theme()

st.markdown('<div class="hero-title">⚡ Deep Research RAG Engine</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Production-grade Retrieval-Augmented Generation over arXiv AI Research Papers</div>', unsafe_allow_html=True)

# Overview Metrics Grid
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric(label="Active Corpus", value="arXiv CS.AI", delta="Indexed")
with col2:
    st.metric(label="Hybrid Retrieval", value="Dense + BM25", delta="RRF Active")
with col3:
    st.metric(label="Reranker Model", value="Cross-Encoder", delta="ms-marco")
with col4:
    st.metric(label="LLM Provider", value="Google Gemini", delta="v1beta")

st.markdown("<br>", unsafe_allow_html=True)

st.markdown(
    """
    <div class="glass-card">
        <h3>🚀 Master System Capabilities</h3>
        <p style="color: #9CA3AF;">Use the left sidebar navigation to explore the deep research suite:</p>
        <ul style="line-height: 1.8; color: #E5E7EB;">
            <li>🔍 <b>Interactive Query Inspector</b> — Run multi-strategy retrieval, inspect reranked context chunks, and generate grounded answers.</li>
            <li>📊 <b>Experiment Benchmark Matrix</b> — Compare side-by-side performance across <code>baseline</code> and <code>full_pipeline</code> runs.</li>
            <li>💬 <b>Active Feedback Analytics</b> — Inspect user ratings (+1 / -1) and track low-scoring paper chunks.</li>
            <li>🛡️ <b>Adversarial Guardrails</b> — View safety evaluation test cases for prompt injection defense.</li>
        </ul>
    </div>
    """,
    unsafe_allow_html=True,
)
