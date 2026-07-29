# 🎛️ ToneShift: Audience-Aware Rewriter

An agentic AI tool that rewrites any text into a chosen tone and audience — with a built-in agent that back-translates and checks its own output for meaning drift, and autonomously retries if it drifts too far.

Built with **Python, LangChain, Groq (LLaMA 3.1 8B Instant), and Streamlit.**

---

## Overview

ToneShift takes any piece of text and rewrites it into one of several tones — Formal, Casual, Child-Friendly, or Executive Summary — with sliders to control length and formality. What makes it more than a prompt wrapper is the **ReWrite Agent**: a small pipeline that plans its rewrite strategy, calls discrete tools, verifies its own output via back-translation, and autonomously retries with stricter constraints if meaning drift is detected.

## Features

- 🎯 Rewrite into 4+ distinct tones from a single input
- 🎚️ Sliders for length (compress ↔ expand) and formality (casual ↔ formal)
- 🔍 Side-by-side comparison view: original vs. rewrite
- 🔄 Automatic back-translation check for meaning preservation
- ⚠️ Drift warning banner with visible agent reasoning trail (retry attempts, scores)
- 🧠 Session memory — revisit and compare past rewrites without re-running

## How the Agent Works

1. **Plan** — chooses an initial rewrite strategy (temperature) based on input length.
2. **Act** — calls `rewrite_tool` to transform the text into the target tone.
3. **Verify** — calls `backtranslate_tool` to independently paraphrase the rewrite, then `drift_score_tool` to measure semantic similarity against the original.
4. **Decide** — if the similarity score falls below the threshold, the agent autonomously retries with stricter fidelity constraints (preserve entities/numbers, lower temperature), up to 2 retries.
5. **Return** — the best-scoring attempt, with a full log of every attempt shown in the UI.

## Architecture

```
Streamlit UI (app.py)
        │
        ▼
ReWrite Agent (agent/rewrite_agent.py)
   - planning + autonomous retry decisions
        │
   ┌────┼─────────────┐
   ▼    ▼              ▼
rewrite  backtranslate  drift_score
 tool       tool           tool
   │         │              │
   └─────────┴──────────────┘
              │
        Groq LLaMA 3.1 API
   (+ local sentence-transformers
      for drift scoring)
```

## Project Structure

```
toneshift/
├── app.py                     # Streamlit entrypoint
├── agent/
│   ├── rewrite_agent.py       # Planning + retry/decision logic
│   └── tools.py                # rewrite_tool, backtranslate_tool, drift_score_tool
├── core/
│   ├── llm_client.py           # Groq LLM wrapper
│   └── config.py                # Tone presets, thresholds, constants
├── ui/
│   └── components.py           # Drift banner, comparison view, history panel
├── assets/
│   └── style.css
├── requirements.txt
└── .env.example
```

## Installation

```bash
git clone <your-repo-url>
cd toneshift
python -m venv venv
source venv/bin/activate       # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

## Environment Variables

Copy `.env.example` to `.env` and add your free Groq API key:

```
GROQ_API_KEY=your_groq_api_key_here
```

Get a free key at [console.groq.com/keys](https://console.groq.com/keys).

## How to Run

```bash
streamlit run app.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`).

## Requirements

See `requirements.txt`. Key dependencies: `streamlit`, `langchain-groq`, `sentence-transformers`, `python-dotenv`.

## Screenshots

_Add screenshots here after running the app:_

`![Main UI](screenshots/main-ui.png)`
`![Drift Warning](screenshots/drift-warning.png)`

## Future Scope

- Persist history to SQLite for cross-session memory
- Support custom/user-defined tones beyond the 4 presets
- Batch rewrite (paste multiple paragraphs, rewrite all at once)
- True back-translation via an actual translation API instead of paraphrase-based approximation
- Multi-language support

## License

MIT License — free to use, modify, and distribute for academic or personal purposes.
