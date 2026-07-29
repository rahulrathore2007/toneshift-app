"""
Thin wrapper around the Groq-backed LangChain chat model.
Keeping this isolated means if we ever swap providers (e.g. to another
free API), only this file changes — nothing else in the app cares.
"""

from langchain_groq import ChatGroq
from core.config import GROQ_API_KEY, GROQ_MODEL


def get_llm(temperature: float = 0.4) -> ChatGroq:
    """
    Returns a configured ChatGroq LLM instance.
    temperature is exposed so callers (e.g. the retry logic) can
    lower it for stricter, less "creative" rewrites.
    """
    if not GROQ_API_KEY:
        raise ValueError(
            "GROQ_API_KEY is not set. Copy .env.example to .env and add your key."
        )
    return ChatGroq(
        api_key=GROQ_API_KEY,
        model=GROQ_MODEL,
        temperature=temperature,
        max_tokens=1024,
    )
