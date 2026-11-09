# MedLucid

Plain-language explanations of medical lab reports for people whose report has flagged values.
The user uploads a report (PDF / photo / pasted text), types their own worry about it, and gets: a calm
overview, each result explained against the report's own reference range, an answer to their concern, and
specific questions to take to their doctor. If every value is in range, they get a short "all clear" instead.

Student project for Digital Product Management (one user segment, one problem, one workflow, one AI capability).

## Run locally
```bash
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .streamlit/secrets.toml.example .streamlit/secrets.toml   # then add your GEMINI_API_KEY
streamlit run app.py
```
Without an API key the app runs in **demo mode**: only the two built-in sample reports work, using
pre-written output (clearly labelled on screen). Useful as a fallback for presentations.

## Deploy (Streamlit Community Cloud)
1. Push this folder to a GitHub repo (do NOT commit `.streamlit/secrets.toml`; it is git-ignored).
2. share.streamlit.io -> New app -> pick the repo, branch, `app.py`.
3. App settings -> Secrets -> add `GEMINI_API_KEY = "..."`.

## Structure
| File | Purpose |
|---|---|
| `app.py` | Streamlit UI and workflow (share report + concern -> results / all clear) |
| `ai.py` | The AI capability: one Gemini call returning structured JSON, with friendly error handling |
| `prompts.py` | System instruction and guardrails |
| `schema.py` | Pydantic schema of the AI output; the UI renders only from this |
| `ui.py` | CSS and HTML builders (cards, range bars) |
| `samples.py` | Synthetic sample reports and demo output |

## Notes
- No database, no login, no file is written to disk; the report lives in memory for the session.
- Model is configurable via `GEMINI_MODEL` (default in `ai.py`). Check it is still available on your key.
- Use the sample or dummy reports for testing. Check your API plan's data-use terms before uploading anything real.

## AI-use disclosure
Code was written with an AI assistant (Claude). The team is responsible for reviewing, running and being
able to explain all code. Product decisions, research analysis and submission text are the team's own.
