"""
The three tools the ReWrite Agent calls. Each is a discrete, single-purpose
function — this is what makes the app "agentic tool calling" rather than
a single prompt-and-print script.

1. rewrite_tool        -> performs the tone transformation
2. backtranslate_tool  -> paraphrases the rewrite independently, to test
                           whether meaning survived the tone change
3. drift_score_tool    -> scores semantic similarity between original and
                           the back-translated paraphrase
"""

from functools import lru_cache
from sentence_transformers import SentenceTransformer, util

from core.llm_client import get_llm
from core.config import TONE_PRESETS, EMBEDDING_MODEL


@lru_cache(maxsize=1)
def _get_embedder() -> SentenceTransformer:
    """Loaded once and cached — embedding model load is the slowest part."""
    return SentenceTransformer(EMBEDDING_MODEL)


def rewrite_tool(
    text: str,
    tone: str,
    length_bias: int,
    formality_bias: int,
    strict_fidelity: bool = False,
    temperature: float = 0.4,
) -> str:
    """
    Rewrites `text` into the target `tone`.

    length_bias: -2 (much shorter) .. +2 (much longer), 0 = same length
    formality_bias: -2 (much more casual) .. +2 (much more formal)
    strict_fidelity: when True, adds hard constraints used during
                      the agent's autonomous retry-on-drift step.
    """
    llm = get_llm(temperature=temperature)
    tone_instruction = TONE_PRESETS.get(tone, TONE_PRESETS["Formal"])

    length_map = {
        -2: "Make it noticeably shorter — compress to the core message.",
        -1: "Make it a bit shorter than the original.",
        0: "Keep it roughly the same length as the original.",
        1: "Make it a bit longer, with slightly more elaboration.",
        2: "Make it noticeably longer, with fuller explanation.",
    }
    formality_map = {
        -2: "Push the formality much more casual than the tone default.",
        -1: "Push the formality slightly more casual than the tone default.",
        0: "Keep the tone's default formality level.",
        1: "Push the formality slightly more formal than the tone default.",
        2: "Push the formality much more formal than the tone default.",
    }

    fidelity_clause = ""
    if strict_fidelity:
        fidelity_clause = (
            "\n\nSTRICT FIDELITY MODE: A previous attempt drifted too far from "
            "the original meaning. This time you MUST preserve every named "
            "entity, number, date, and factual claim exactly. Do not add "
            "information that isn't in the source. Do not remove key facts. "
            "Only the style/tone/length may change."
        )

    prompt = (
        f"{tone_instruction}\n"
        f"{length_map.get(length_bias, length_map[0])}\n"
        f"{formality_map.get(formality_bias, formality_map[0])}"
        f"{fidelity_clause}\n\n"
        f"Original text:\n\"\"\"\n{text}\n\"\"\"\n\n"
        f"Return ONLY the rewritten text, with no preamble, no quotes, "
        f"and no explanation."
    )

    response = llm.invoke(prompt)
    return response.content.strip()


def backtranslate_tool(rewritten_text: str, temperature: float = 0.3) -> str:
    """
    Independently paraphrases the rewrite back into plain, neutral English.
    This acts as a stand-in for a literal back-translation (translate to
    another language and back) — it forces the model to re-derive the
    underlying meaning from the rewrite alone, with no memory of the
    original, which is exactly what we need to test for drift.
    """
    llm = get_llm(temperature=temperature)
    prompt = (
        "Paraphrase the following text in plain, neutral English. "
        "Do not preserve its tone or style — just restate its literal "
        "factual content as directly and simply as possible.\n\n"
        f"Text:\n\"\"\"\n{rewritten_text}\n\"\"\"\n\n"
        "Return ONLY the paraphrase, nothing else."
    )
    response = llm.invoke(prompt)
    return response.content.strip()


def drift_score_tool(original_text: str, backtranslated_text: str) -> float:
    """
    Computes cosine similarity between embeddings of the original text
    and the back-translated paraphrase. Returns a float in [0, 1] —
    higher means meaning was preserved better.
    """
    embedder = _get_embedder()
    embeddings = embedder.encode(
        [original_text, backtranslated_text], convert_to_tensor=True
    )
    score = util.cos_sim(embeddings[0], embeddings[1]).item()
    # cos_sim can technically be slightly negative for unrelated text;
    # clamp to [0, 1] for a clean UI display.
    return max(0.0, min(1.0, score))
