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
    from dashboard.components.styles import apply_master_theme
except ImportError:
    from components.styles import apply_master_theme

st.set_page_config(page_title="Feedback Analytics", page_icon="💬", layout="wide")
apply_master_theme()

st.markdown('<div class="hero-title">💬 Active Feedback Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">User rating distribution, lowest-scoring queries, and problematic paper chunks</div>', unsafe_allow_html=True)

API_URL = os.getenv("API_URL", "http://localhost:8000")

try:
    resp = httpx.get(f"{API_URL}/feedback/analytics", timeout=10.0)
    if resp.status_code == 200:
        data = resp.json()
        st.subheader("Lowest-Rated Queries")
        st.json(data.get("lowest_rated_queries", []))

        st.subheader("Chunks Associated with Negative Feedback")
        st.json(data.get("problematic_chunks", []))
    else:
        st.warning(f"Could not load feedback analytics: {resp.status_code}")
except Exception as e:
    st.info("No active API server connection or feedback data available.")
