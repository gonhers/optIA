# Prompt Optimizer SaaS

Simple full-stack SaaS demo with:

- FastAPI backend
- React frontend
- Tailwind CSS styling
- Simulated or live response generation and scoring

## Run

1. Create a virtual environment:

   ```powershell
   python -m venv .venv
   ```

2. Install backend dependencies:

   ```powershell
   .\.venv\Scripts\python -m pip install -r backend\requirements.txt
   ```

3. Start the app:

   ```powershell
   .\.venv\Scripts\python -m uvicorn backend.app.main:app --reload
   ```

4. Open [http://127.0.0.1:8000](http://127.0.0.1:8000)

## API

`POST /optimize`

```json
{
  "prompt": "Create a crisp launch message for a B2B SaaS tool.",
  "target_language": "es",
  "candidate_count": 5
}
```

Supported `target_language` codes:

- `es`
- `en`
- `fr`
- `zh`
- `pt`
- `ja`
- `it`

## Live LLM Mode

The app supports a real provider in addition to simulation mode.

Configure these values in `.env`:

- `LLM_MODE=live`
- `LLM_API_KEY=...`
- `LLM_BASE_URL=...`
- `LLM_MODEL=...`

The live integration uses an OpenAI-compatible `chat/completions` API shape.
