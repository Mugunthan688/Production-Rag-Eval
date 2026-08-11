import sys
from pathlib import Path

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

import streamlit as st
import json
import httpx
import os

from dashboard.components.styles import apply_master_theme

st.set_page_config(page_title="Adversarial Guardrails", page_icon="🛡️", layout="wide")
apply_master_theme()

st.markdown('<div class="hero-title">🛡️ Security Guardrails & Safety</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-subtitle">Prompt injection evaluation and system prompt leak defense test cases</div>', unsafe_allow_html=True)

adv_file = root_dir / "data" / "adversarial_set.json"

if adv_file.exists():
    with open(adv_file, "r", encoding="utf-8") as f:
        cases = json.load(f)
    st.success(f"Loaded {len(cases)} adversarial test cases scaffolding from `data/adversarial_set.json`")
    st.json(cases)
else:
    st.info("No `data/adversarial_set.json` file found. User will supply 10-15 prompt injection & system leak test cases.")

