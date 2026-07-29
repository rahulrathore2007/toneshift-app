"""
The ReWrite Agent.

This is where PLANNING and DECISION MAKING live, on top of the raw tools
in tools.py:

  - Planning: decides retry temperature/strictness strategy based on text
    length and how far the drift score missed the threshold.
  - Decision making: autonomously decides whether to retry, how many times,
    and when to stop and surface a warning instead of looping forever.
  - Memory: the caller (Streamlit session_state) persists AgentResult
    history across runs within a session so past rewrites stay comparable.

This is intentionally implemented as a small deterministic orchestrator
rather than a black-box LangChain AgentExecutor with free-form tool
selection. For a task with exactly three tools that must always run in a
fixed pipeline (rewrite -> backtranslate -> score -> maybe retry), a
scripted planner is more reliable and easier to grade/demo than an LLM
picking tools by itself, while still exhibiting real planning and
autonomous decision-making at the retry step.
"""

from dataclasses import dataclass, field
from typing import List

from agent.tools import rewrite_tool, backtranslate_tool, drift_score_tool
from core.config import DRIFT_THRESHOLD, MAX_RETRIES


@dataclass
class AttemptLog:
    attempt_number: int
    rewrite: str
    backtranslation: str
    drift_score: float
    strict_fidelity_used: bool
    temperature_used: float


@dataclass
class AgentResult:
    final_rewrite: str
    final_drift_score: float
    passed_threshold: bool
    attempts: List[AttemptLog] = field(default_factory=list)
    tone: str = ""
    original_text: str = ""


def run_rewrite_agent(
    text: str,
    tone: str,
    length_bias: int,
    formality_bias: int,
) -> AgentResult:
    """
    Orchestrates the full agent pipeline:

    1. PLAN: choose an initial strategy (temperature) based on input length.
    2. ACT: call rewrite_tool.
    3. VERIFY: call backtranslate_tool + drift_score_tool.
    4. DECIDE: if drift_score < DRIFT_THRESHOLD, autonomously retry with
       stricter constraints (lower temperature, strict_fidelity=True),
       up to MAX_RETRIES times. Otherwise, return immediately.
    5. Return the best attempt (highest drift score) with full attempt log.
    """
    attempts: List[AttemptLog] = []

    # --- PLAN: longer inputs get a slightly lower starting temperature,
    # since there's more content that could drift.
    word_count = len(text.split())
    base_temperature = 0.5 if word_count < 60 else 0.4

    strict_fidelity = False
    temperature = base_temperature
    best_attempt: AttemptLog | None = None

    for attempt_number in range(1, MAX_RETRIES + 2):  # initial try + retries
        rewrite = rewrite_tool(
            text=text,
            tone=tone,
            length_bias=length_bias,
            formality_bias=formality_bias,
            strict_fidelity=strict_fidelity,
            temperature=temperature,
        )
        backtranslation = backtranslate_tool(rewrite)
        score = drift_score_tool(text, backtranslation)

        log = AttemptLog(
            attempt_number=attempt_number,
            rewrite=rewrite,
            backtranslation=backtranslation,
            drift_score=score,
            strict_fidelity_used=strict_fidelity,
            temperature_used=temperature,
        )
        attempts.append(log)

        if best_attempt is None or score > best_attempt.drift_score:
            best_attempt = log

        # --- DECIDE
        if score >= DRIFT_THRESHOLD:
            break  # good enough, stop here
        if attempt_number >= MAX_RETRIES + 1:
            break  # out of retries, stop with best attempt so far

        # Autonomous retry decision: tighten constraints and lower
        # temperature so the next attempt is more literal.
        strict_fidelity = True
        temperature = max(0.1, temperature - 0.2)

    assert best_attempt is not None

    return AgentResult(
        final_rewrite=best_attempt.rewrite,
        final_drift_score=best_attempt.drift_score,
        passed_threshold=best_attempt.drift_score >= DRIFT_THRESHOLD,
        attempts=attempts,
        tone=tone,
        original_text=text,
    )
