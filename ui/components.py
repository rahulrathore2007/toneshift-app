"""
Reusable Streamlit UI components, kept separate from app.py so the
main app file stays focused on layout/flow rather than rendering details.
"""

import streamlit as st
from agent.rewrite_agent import AgentResult


def render_drift_banner(result: AgentResult) -> None:
    """Shows a colored banner reflecting meaning-preservation confidence."""
    score_pct = round(result.final_drift_score * 100, 1)

    if result.passed_threshold:
        st.success(f"✅ Meaning preserved — similarity score **{score_pct}%**")
    else:
        st.error(
            f"⚠️ Possible meaning drift detected — similarity score "
            f"**{score_pct}%** is below the safe threshold. "
            f"The best available attempt (out of {len(result.attempts)}) "
            f"is shown below. Consider simplifying the source text or "
            f"choosing a less extreme tone/length setting."
        )

    if len(result.attempts) > 1:
        with st.expander(f"🔁 Agent made {len(result.attempts)} attempts — see reasoning trail"):
            for a in result.attempts:
                mode = "strict fidelity retry" if a.strict_fidelity_used else "initial attempt"
                st.markdown(
                    f"**Attempt {a.attempt_number}** ({mode}, temp={a.temperature_used}) "
                    f"— drift score: `{round(a.drift_score * 100, 1)}%`"
                )


def render_comparison_view(result: AgentResult) -> None:
    """Side-by-side original vs. rewrite, plus the back-translation check."""
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Original")
        st.text_area(
            "original_display",
            value=result.original_text,
            height=220,
            disabled=True,
            label_visibility="collapsed",
        )
    with col2:
        st.markdown(f"#### Rewritten — {result.tone}")
        st.text_area(
            "rewrite_display",
            value=result.final_rewrite,
            height=220,
            disabled=True,
            label_visibility="collapsed",
        )

    with st.expander("🔄 Back-translation (used internally to check meaning drift)"):
        best = max(result.attempts, key=lambda a: a.drift_score)
        st.write(best.backtranslation)


def render_history_panel(history: list) -> None:
    """Session-memory panel: lets user revisit/compare past rewrites."""
    if not history:
        st.caption("No rewrites yet this session.")
        return

    for i, past_result in enumerate(reversed(history)):
        label = f"{past_result.tone} — \"{past_result.original_text[:40]}...\""
        with st.expander(label):
            st.markdown(f"**Drift score:** {round(past_result.final_drift_score * 100, 1)}%")
            st.write(past_result.final_rewrite)
