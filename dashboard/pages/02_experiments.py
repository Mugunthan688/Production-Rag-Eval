import sys
from pathlib import Path

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import json
import pandas as pd
from src.evaluation.comparator import build_comparison_dataframe

try:
    from dashboard.components.metrics_table import render_metrics_table
    from dashboard.components.styles import apply_master_theme
except ImportError:
    from components.metrics_table import render_metrics_table
    from components.styles import apply_master_theme

st.set_page_config(page_title="Experiment Comparison", page_icon="📊", layout="wide")
apply_master_theme()

st.markdown('<div class="hero-title">📊 Experiment Benchmark Matrix</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Quantitative comparison of precision, recall, MRR, faithfulness, and latency</div>', unsafe_allow_html=True)

df = build_comparison_dataframe()
render_metrics_table(df)
