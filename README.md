# optIA

Prompt optimizer SaaS demo with a FastAPI backend, React frontend, Tailwind CSS styling, and simulated or live response generation and scoring.

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

## Deploy rápido en Render

La forma más simple de dejar esta demo online es usar Render como un solo servicio web. Este repo ya incluye un archivo [render.yaml](./render.yaml) listo para deploy.

### Pasos

1. Entrá a [Render](https://render.com/).
2. Elegí `New` -> `Blueprint`.
3. Conectá tu GitHub y seleccioná este repo: `gonhers/optIA`.
4. Render va a detectar automáticamente `render.yaml`.
5. Confirmá el deploy.
6. Cuando termine, te va a dar una URL pública `onrender.com`.

### Configuración usada

- Build command: `pip install -r backend/requirements.txt`
- Start command: `uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT`

### Nota

En este momento la app puede publicarse directamente en `simulation mode`, así que no necesitás variables de entorno para mostrarla.
