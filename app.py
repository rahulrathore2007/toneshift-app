"""
ToneShift: Audience-Aware Rewriter — Streamlit entrypoint.

Run with: streamlit run app.py
"""

import streamlit as st

from core.config import TONE_PRESETS
from agent.rewrite_agent import run_rewrite_agent
from ui.components import render_drift_banner, render_comparison_view, render_history_panel

st.set_page_config(
    page_title="ToneShift — Audience-Aware Rewriter",
    page_icon="🎛️",
    layout="wide",
)

# --- Load custom CSS ---
try:
    with open("assets/style.css") as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
except FileNotFoundError:
    pass

# --- Session memory: keeps prior rewrites available for comparison ---
if "history" not in st.session_state:
    st.session_state.history = []

# --- Header ---
st.title("🎛️ ToneShift")
st.caption("Audience-Aware Rewriter — powered by a tool-calling, self-checking rewrite agent")

# --- Input ---
source_text = st.text_area(
    "Paste the text you want to transform",
    height=180,
    placeholder="Paste an email, paragraph, announcement, or any text here...",
)

col_a, col_b, col_c = st.columns([1.2, 1, 1])
with col_a:
    tone = st.selectbox("Target tone / audience", list(TONE_PRESETS.keys()))
with col_b:
    length_bias = st.slider("Length", -2, 2, 0, help="-2 = much shorter, +2 = much longer")
with col_c:
    formality_bias = st.slider("Formality", -2, 2, 0, help="-2 = more casual, +2 = more formal")

run_clicked = st.button("✨ Rewrite", use_container_width=False)

st.divider()

# --- Run the agent ---
if run_clicked:
    if not source_text.strip():
        st.warning("Please paste some text first.")
    else:
        with st.spinner("Agent is rewriting, back-translating, and checking meaning drift..."):
            try:
                result = run_rewrite_agent(
                    text=source_text,
                    tone=tone,
                    length_bias=length_bias,
                    formality_bias=formality_bias,
                )
                st.session_state.history.append(result)
                st.session_state.latest_result = result
            except ValueError as e:
                st.error(str(e))

# --- Display latest result ---
if "latest_result" in st.session_state:
    result = st.session_state.latest_result
    render_drift_banner(result)
    render_comparison_view(result)

# --- History panel ---
st.divider()
st.subheader("📜 Session History")
render_history_panel(st.session_state.history)
