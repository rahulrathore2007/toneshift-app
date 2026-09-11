"""
Central configuration for ToneShift.
Holds tone definitions, thresholds, and model settings so nothing
is hardcoded/scattered across the app.
"""

import os
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL = "openai/gpt-oss-20b"

# Minimum acceptable semantic similarity (0-1) between the original text
# and the back-translated rewrite before we flag "meaning drift".
DRIFT_THRESHOLD = 0.72

# How many times the agent will autonomously retry a rewrite with
# stricter fidelity constraints before giving up and showing the
# best attempt with a warning.
MAX_RETRIES = 2

# Tone presets: each has a system-style instruction the rewrite_tool uses.
TONE_PRESETS = {
    "Formal": (
        "Rewrite the text in a formal, professional register. Use complete "
        "sentences, precise vocabulary, and avoid contractions or slang."
    ),
    "Casual": (
        "Rewrite the text in a relaxed, conversational tone, as if explaining "
        "it to a friend. Contractions and simple everyday words are welcome."
    ),
    "Child-Friendly": (
        "Rewrite the text so a curious 8-year-old could understand it. Use "
        "short sentences, simple words, and a friendly, encouraging tone. "
        "Avoid jargon; explain any concept simply if it can't be removed."
    ),
    "Executive Summary": (
        "Rewrite the text as a concise executive summary for a busy "
        "decision-maker. Lead with the key takeaway, use crisp language, "
        "and prioritize actionable points over background detail."
    ),
}

# Embedding model used for local, free semantic similarity scoring.
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
