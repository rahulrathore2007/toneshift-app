# GitHub Setup Guide — ToneShift

Use this as a checklist while creating and pushing the repository.

---

## Repository Description (short, for the GitHub "About" field)

```
🎛️ ToneShift — an agentic AI rewriter that transforms text into different tones (formal, casual, child-friendly, executive) and self-checks meaning preservation via back-translation drift scoring. Built with LangChain + Groq + Streamlit.
```

## Topics (add under repo "About" → gear icon → Topics)

```
python
streamlit
langchain
groq
llm
agentic-ai
ai-agent
tone-transformation
nlp
llama3
generative-ai
text-rewriting
```

## Suggested Commit Sequence

If committing incrementally (recommended — shows real development history rather than one giant dump):

```
git init
git add requirements.txt .env.example .gitignore
git commit -m "chore: project scaffolding, dependencies, env template"

git add core/
git commit -m "feat: add config and Groq LLM client wrapper"

git add agent/tools.py
git commit -m "feat: add rewrite, backtranslate, and drift-score tools"

git add agent/rewrite_agent.py
git commit -m "feat: add ReWrite Agent with planning and autonomous retry logic"

git add ui/
git commit -m "feat: add Streamlit UI components (drift banner, comparison view, history)"

git add app.py assets/
git commit -m "feat: wire up Streamlit entrypoint and custom styling"

git add README.md
git commit -m "docs: add README with setup and architecture overview"

git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

If you're short on time and pushing everything at once, a single commit is acceptable too:

```
git init
git add .
git commit -m "feat: initial implementation of ToneShift agentic rewriter"
git branch -M main
git remote add origin <your-repo-url>
git push -u origin main
```

## Release Notes — v1.0.0

```markdown
## ToneShift v1.0.0 — Initial Release

### Features
- Rewrite input text into 4 tones: Formal, Casual, Child-Friendly, Executive Summary
- Length and formality sliders for fine-grained control
- Agentic pipeline: rewrite → back-translate → drift-score → autonomous retry on low fidelity
- Side-by-side original vs. rewrite comparison view
- Drift warning banner with visible agent reasoning trail
- Session-based rewrite history

### Tech Stack
- Python 3.10+
- Streamlit (UI)
- LangChain + langchain-groq (LLM orchestration)
- Groq LLaMA 3.1 8B Instant (free-tier inference)
- sentence-transformers (local embedding-based drift scoring)

### Known Limitations
- Back-translation is approximated via independent paraphrasing rather than a literal
  translate-out/translate-back through another language.
- History is in-memory only (resets on app restart); no persistent storage yet.
- Tone presets are fixed to 4 options in this release.
```

## .gitignore (already included in repo root)

Confirms `.env`, `__pycache__/`, and virtual environment folders are excluded so no secrets or bulky artifacts get committed.
